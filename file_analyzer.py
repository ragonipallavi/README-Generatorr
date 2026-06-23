import os
import json
import re

IGNORE_DIRS = {'.git', 'node_modules', '__pycache__', '.next', 'dist', 'build',
               'venv', '.venv', 'env', '.env', 'coverage', '.pytest_cache',
               '.mypy_cache', 'eggs', '.eggs', '*.egg-info'}

IGNORE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.svg', '.ico', '.woff',
                     '.woff2', '.ttf', '.eot', '.mp4', '.mp3', '.zip', '.tar',
                     '.gz', '.pdf', '.lock', '.map'}

TEXT_EXTENSIONS = {'.py', '.js', '.ts', '.jsx', '.tsx', '.html', '.css', '.scss',
                   '.json', '.yaml', '.yml', '.toml', '.md', '.txt', '.env',
                   '.sh', '.bash', '.rb', '.go', '.rs', '.java', '.kt', '.swift',
                   '.php', '.cs', '.cpp', '.c', '.h', '.dockerfile', '.sql',
                   '.graphql', '.prisma', '.xml', '.conf', '.cfg', '.ini'}

PRIORITY_FILES = {'package.json', 'requirements.txt', 'pyproject.toml', 'go.mod',
                  'Cargo.toml', 'pom.xml', 'build.gradle', 'Gemfile', 'Dockerfile',
                  'docker-compose.yml', 'docker-compose.yaml', '.env.example',
                  'README.md', 'setup.py', 'setup.cfg', 'composer.json',
                  'pubspec.yaml', 'Makefile', 'main.py', 'app.py', 'index.js',
                  'index.ts', 'server.js', 'server.ts', 'manage.py', 'wsgi.py'}


def build_folder_structure(base_path: str, max_depth: int = 3) -> str:
    lines = []

    def walk(path, prefix="", depth=0):
        if depth > max_depth:
            return
        try:
            entries = sorted(os.listdir(path))
        except PermissionError:
            return

        entries = [e for e in entries if e not in IGNORE_DIRS and not e.startswith('.')]
        dirs = [e for e in entries if os.path.isdir(os.path.join(path, e))]
        files = [e for e in entries if os.path.isfile(os.path.join(path, e))]

        all_entries = dirs + files
        for i, entry in enumerate(all_entries):
            is_last = i == len(all_entries) - 1
            connector = "└── " if is_last else "├── "
            lines.append(f"{prefix}{connector}{entry}")
            full_path = os.path.join(path, entry)
            if os.path.isdir(full_path):
                extension = "    " if is_last else "│   "
                walk(full_path, prefix + extension, depth + 1)

    folder_name = os.path.basename(base_path) or "project"
    lines.append(f"{folder_name}/")
    walk(base_path)
    return "\n".join(lines[:80])  # Cap at 80 lines


def read_project_files(base_path: str, max_files: int = 30) -> dict:
    file_contents = {}
    priority_found = []
    other_files = []

    for root, dirs, files in os.walk(base_path):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS and not d.startswith('.')]
        for fname in files:
            fpath = os.path.join(root, fname)
            rel_path = os.path.relpath(fpath, base_path)
            ext = os.path.splitext(fname)[1].lower()
            if ext in IGNORE_EXTENSIONS:
                continue
            if fname in PRIORITY_FILES:
                priority_found.append((rel_path, fpath))
            elif ext in TEXT_EXTENSIONS:
                other_files.append((rel_path, fpath))

    selected = priority_found + other_files
    selected = selected[:max_files]

    for rel_path, fpath in selected:
        try:
            with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(3000)
                file_contents[rel_path] = content
        except Exception:
            pass

    return file_contents


def analyze_project(file_contents: dict) -> dict:
    result = {
        "languages": set(),
        "frameworks": set(),
        "databases": set(),
        "dependencies": [],
        "has_docker": False,
        "has_cicd": False,
        "api_endpoints": [],
        "env_vars": [],
        "project_type": "fullstack"
    }

    all_text = "\n".join(file_contents.values()).lower()

    # Languages
    ext_lang_map = {
        '.py': 'Python', '.js': 'JavaScript', '.ts': 'TypeScript',
        '.jsx': 'JavaScript (React)', '.tsx': 'TypeScript (React)',
        '.go': 'Go', '.rs': 'Rust', '.java': 'Java', '.rb': 'Ruby',
        '.php': 'PHP', '.cs': 'C#', '.cpp': 'C++', '.swift': 'Swift',
        '.kt': 'Kotlin'
    }
    for path in file_contents:
        ext = os.path.splitext(path)[1].lower()
        if ext in ext_lang_map:
            result["languages"].add(ext_lang_map[ext])

    # Frameworks
    framework_signals = {
        'react': 'React', 'next': 'Next.js', 'vue': 'Vue.js', 'angular': 'Angular',
        'express': 'Express.js', 'fastapi': 'FastAPI', 'flask': 'Flask',
        'django': 'Django', 'spring': 'Spring Boot', 'rails': 'Ruby on Rails',
        'svelte': 'Svelte', 'nuxt': 'Nuxt.js', 'nestjs': 'NestJS',
        'laravel': 'Laravel', 'gin': 'Gin', 'fiber': 'Fiber',
        'pytorch': 'PyTorch', 'tensorflow': 'TensorFlow', 'sklearn': 'Scikit-learn',
        'langchain': 'LangChain', 'streamlit': 'Streamlit'
    }
    for signal, name in framework_signals.items():
        if signal in all_text:
            result["frameworks"].add(name)

    # Databases
    db_signals = {
        'mongodb': 'MongoDB', 'mongoose': 'MongoDB', 'postgresql': 'PostgreSQL',
        'postgres': 'PostgreSQL', 'mysql': 'MySQL', 'sqlite': 'SQLite',
        'redis': 'Redis', 'elasticsearch': 'Elasticsearch', 'supabase': 'Supabase',
        'prisma': 'Prisma', 'sequelize': 'Sequelize', 'sqlalchemy': 'SQLAlchemy',
        'firebase': 'Firebase'
    }
    for signal, name in db_signals.items():
        if signal in all_text:
            result["databases"].add(name)

    # Docker & CI/CD
    if 'dockerfile' in [os.path.basename(p).lower() for p in file_contents]:
        result["has_docker"] = True
    if any('.github' in p or 'gitlab-ci' in p or 'jenkinsfile' in p.lower() for p in file_contents):
        result["has_cicd"] = True

    # Dependencies from package.json
    for path, content in file_contents.items():
        if 'package.json' in path:
            try:
                pkg = json.loads(content)
                deps = list(pkg.get('dependencies', {}).keys()) + list(pkg.get('devDependencies', {}).keys())
                result["dependencies"].extend(deps[:20])
            except Exception:
                pass
        if 'requirements.txt' in path:
            lines = [l.split('==')[0].split('>=')[0].strip() for l in content.split('\n') if l.strip() and not l.startswith('#')]
            result["dependencies"].extend(lines[:20])

    # API endpoints
    route_patterns = [
        r"@app\.(get|post|put|delete|patch)\(['\"]([^'\"]+)['\"]",
        r"router\.(get|post|put|delete|patch)\(['\"]([^'\"]+)['\"]",
        r"app\.(get|post|put|delete|patch)\(['\"]([^'\"]+)['\"]",
    ]
    for content in file_contents.values():
        for pattern in route_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for method, path in matches:
                result["api_endpoints"].append(f"{method.upper()} {path}")

    # Environment variables
    for path, content in file_contents.items():
        if '.env' in path.lower():
            for line in content.split('\n'):
                if '=' in line and not line.startswith('#'):
                    var = line.split('=')[0].strip()
                    if var:
                        result["env_vars"].append(var)

    # Project type inference
    has_frontend = bool(result["frameworks"] & {'React', 'Next.js', 'Vue.js', 'Angular', 'Svelte', 'Nuxt.js'})
    has_backend = bool(result["frameworks"] & {'FastAPI', 'Flask', 'Django', 'Express.js', 'NestJS', 'Spring Boot'})
    if has_frontend and has_backend:
        result["project_type"] = "fullstack"
    elif has_frontend:
        result["project_type"] = "frontend"
    elif has_backend:
        result["project_type"] = "backend"

    result["languages"] = list(result["languages"])
    result["frameworks"] = list(result["frameworks"])
    result["databases"] = list(result["databases"])
    result["api_endpoints"] = list(set(result["api_endpoints"]))[:10]
    result["env_vars"] = list(set(result["env_vars"]))[:15]
    result["dependencies"] = list(set(result["dependencies"]))[:20]

    return result


def summarize_files(file_contents: dict, max_chars: int = 12000) -> str:
    summary_parts = []
    total = 0
    # Priority files first
    for fname in PRIORITY_FILES:
        for path, content in file_contents.items():
            if os.path.basename(path) == fname:
                snippet = f"--- {path} ---\n{content[:800]}\n"
                if total + len(snippet) < max_chars:
                    summary_parts.append(snippet)
                    total += len(snippet)

    # Remaining files
    for path, content in file_contents.items():
        if os.path.basename(path) not in PRIORITY_FILES:
            snippet = f"--- {path} ---\n{content[:400]}\n"
            if total + len(snippet) < max_chars:
                summary_parts.append(snippet)
                total += len(snippet)
            else:
                break

    return "\n".join(summary_parts)
