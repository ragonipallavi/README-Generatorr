import os
import requests
import base64
import re

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

IGNORE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.svg', '.ico', '.woff',
                     '.woff2', '.ttf', '.eot', '.mp4', '.mp3', '.zip', '.tar',
                     '.gz', '.pdf', '.lock', '.map', '.min.js', '.min.css'}

MAX_FILE_SIZE = 100 * 1024  # 100KB
MAX_FILES = 30


def parse_github_url(url: str) -> tuple:
    patterns = [
        r"github\.com/([^/]+)/([^/\s?#]+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            owner = match.group(1)
            repo = match.group(2).rstrip('.git')
            return owner, repo
    raise ValueError(f"Invalid GitHub URL: {url}")


def fetch_github_tree(owner: str, repo: str, branch: str = None) -> list:
    headers = {"Accept": "application/vnd.github.v3+json"}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"

    # Get default branch if not specified
    if not branch:
        repo_resp = requests.get(
            f"https://api.github.com/repos/{owner}/{repo}",
            headers=headers, timeout=15
        )
        if repo_resp.status_code == 404:
            raise Exception(f"Repository '{owner}/{repo}' not found or is private.")
        repo_resp.raise_for_status()
        branch = repo_resp.json().get("default_branch", "main")

    # Get file tree
    tree_resp = requests.get(
        f"https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}?recursive=1",
        headers=headers, timeout=15
    )
    tree_resp.raise_for_status()
    tree = tree_resp.json().get("tree", [])
    return [item for item in tree if item.get("type") == "blob"]


def fetch_file_content(owner: str, repo: str, path: str) -> str:
    headers = {"Accept": "application/vnd.github.v3+json"}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"

    resp = requests.get(
        f"https://api.github.com/repos/{owner}/{repo}/contents/{path}",
        headers=headers, timeout=10
    )
    if resp.status_code != 200:
        return None

    data = resp.json()
    if data.get("encoding") == "base64":
        try:
            return base64.b64decode(data["content"]).decode("utf-8", errors="ignore")
        except Exception:
            return None
    return None


def fetch_github_repo(url: str) -> dict:
    owner, repo = parse_github_url(url)

    tree = fetch_github_tree(owner, repo)

    # Filter and prioritize files
    priority_names = {'package.json', 'requirements.txt', 'Dockerfile', 'docker-compose.yml',
                      '.env.example', 'setup.py', 'go.mod', 'Cargo.toml', 'README.md',
                      'main.py', 'app.py', 'index.js', 'index.ts', 'server.js'}

    def should_include(item):
        path = item["path"]
        parts = path.split('/')
        ignore_dirs = {'node_modules', '.git', '__pycache__', 'dist', 'build', '.next', 'venv'}
        if any(p in ignore_dirs for p in parts):
            return False
        ext = os.path.splitext(path)[1].lower()
        if ext in IGNORE_EXTENSIONS:
            return False
        if item.get("size", 0) > MAX_FILE_SIZE:
            return False
        return True

    filtered = [item for item in tree if should_include(item)]
    priority = [item for item in filtered if os.path.basename(item["path"]) in priority_names]
    others = [item for item in filtered if os.path.basename(item["path"]) not in priority_names]

    selected = priority + others
    selected = selected[:MAX_FILES]

    file_contents = {}
    for item in selected:
        content = fetch_file_content(owner, repo, item["path"])
        if content:
            file_contents[item["path"]] = content[:3000]

    # Build folder structure from tree
    def build_tree_string():
        paths = [item["path"] for item in tree[:100]]
        lines = [f"{repo}/"]
        shown = set()
        for path in sorted(paths):
            parts = path.split('/')
            for i, part in enumerate(parts):
                key = '/'.join(parts[:i+1])
                if key not in shown:
                    indent = "  " * i
                    lines.append(f"{indent}{'└── ' if i < len(parts)-1 else '├── '}{part}")
                    shown.add(key)
        return "\n".join(lines[:60])

    return {
        "name": repo,
        "owner": owner,
        "file_contents": file_contents,
        "folder_structure": build_tree_string()
    }
