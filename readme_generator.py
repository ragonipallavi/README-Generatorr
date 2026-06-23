from utils.prompts import build_readme_prompt, build_analysis_prompt
from utils.file_analyzer import analyze_project, summarize_files, build_folder_structure
from services.ollama_service import generate_with_ollama
from services.groq_service import generate_with_groq
import json
import re


def _clean_json_response(text: str) -> dict:
    # Try to extract JSON from markdown code blocks
    patterns = [
        r'```json\s*(.*?)\s*```',
        r'```\s*(.*?)\s*```',
        r'\{.*\}'
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1) if '```' in pattern else match.group(0))
            except Exception:
                continue
    raise ValueError("Could not parse JSON from AI response")


def generate_readme(
    file_contents: dict,
    folder_structure: str,
    project_name: str,
    tone: str,
    include_tags: bool,
    template: str,
    ai_provider: str,
    ai_model: str,
    groq_api_key: str = None
) -> str:

    # Step 1: Analyze project files locally
    local_analysis = analyze_project(file_contents)
    local_analysis["name"] = project_name
    local_analysis["folder_structure"] = folder_structure

    # Step 2: Summarize file contents for AI
    file_summary = summarize_files(file_contents)
    local_analysis["file_contents_summary"] = file_summary

    # Step 3: Try AI-enhanced analysis for better results
    try:
        analysis_prompt = build_analysis_prompt(file_summary)
        if ai_provider == "ollama":
            analysis_json_str = generate_with_ollama(analysis_prompt, ai_model)
        else:
            analysis_json_str = generate_with_groq(analysis_prompt, ai_model, groq_api_key)

        ai_analysis = _clean_json_response(analysis_json_str)

        # Merge AI analysis with local analysis
        for key in ["languages", "frameworks", "databases", "api_endpoints", "env_vars"]:
            if ai_analysis.get(key):
                combined = list(set(local_analysis.get(key, []) + ai_analysis.get(key, [])))
                local_analysis[key] = combined

        if ai_analysis.get("name") and ai_analysis["name"] != "Unknown Project":
            local_analysis["name"] = ai_analysis["name"]
        if ai_analysis.get("project_type"):
            local_analysis["project_type"] = ai_analysis["project_type"]
        if ai_analysis.get("dependencies"):
            local_analysis["dependencies"] = list(set(
                local_analysis.get("dependencies", []) + ai_analysis.get("dependencies", [])
            ))[:25]

    except Exception:
        # Use local analysis only if AI analysis fails
        pass

    # Step 4: Generate full README
    readme_prompt = build_readme_prompt(local_analysis, tone, include_tags, template)

    if ai_provider == "ollama":
        readme = generate_with_ollama(readme_prompt, ai_model)
    else:
        readme = generate_with_groq(readme_prompt, ai_model, groq_api_key)

    return readme.strip()
