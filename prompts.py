def build_readme_prompt(project_data: dict, tone: str, include_tags: bool, template: str = None) -> str:
    tone_instructions = {
        "friendly": "Use a warm, welcoming, and enthusiastic tone. Add emojis where appropriate. Make it inviting for contributors.",
        "professional": "Use a formal, polished, corporate-style tone. Keep it concise and businesslike.",
        "technical": "Use precise technical language. Focus on implementation details, architecture, and developer-facing information.",
        "startup": "Use energetic, bold startup language. Highlight innovation, impact, and vision. Be punchy and exciting.",
        "beginner_friendly": "Use simple, clear language. Explain technical terms. Include extra context for newcomers to the project.",
        "minimal": "Be extremely concise. Only include essential information. No fluff, no excessive sections."
    }

    tone_text = tone_instructions.get(tone, tone_instructions["professional"])

    template_hints = {
        "opensource": "This is an open source project. Emphasize contribution guidelines, community, and license prominently.",
        "startup": "This is a startup product. Focus on problem statement, value proposition, and getting started quickly.",
        "portfolio": "This is a portfolio project. Highlight skills demonstrated, technologies used, and what was learned.",
        "aiml": "This is an AI/ML project. Include model details, dataset info, training instructions, and evaluation metrics.",
        "college": "This is a college/academic project. Include project context, learning objectives, and academic disclaimers.",
        "api": "This is an API project. Prioritize endpoint documentation, request/response examples, and authentication details."
    }

    template_hint = ""
    if template and template in template_hints:
        template_hint = f"\n\nTemplate Context: {template_hints[template]}"

    tags_instruction = ""
    if include_tags:
        tags_instruction = "\n\nInclude relevant topic tags/badges at the top of the README (e.g., ![Python](badge_url), ![License](badge_url), etc.) using shields.io badges."

    project_info = f"""
Project Name: {project_data.get('name', 'Unknown Project')}
Detected Language(s): {', '.join(project_data.get('languages', ['Unknown']))}
Detected Frameworks: {', '.join(project_data.get('frameworks', []))}
Detected Databases: {', '.join(project_data.get('databases', []))}
Project Type: {project_data.get('project_type', 'Unknown')}
Dependencies: {', '.join(project_data.get('dependencies', [])[:20])}
Has Docker: {project_data.get('has_docker', False)}
Has CI/CD: {project_data.get('has_cicd', False)}
API Endpoints Detected: {', '.join(project_data.get('api_endpoints', [])[:10])}
Environment Variables: {', '.join(project_data.get('env_vars', [])[:15])}
Folder Structure:
{project_data.get('folder_structure', 'Not available')}
File Contents Summary:
{project_data.get('file_contents_summary', 'Not available')}
"""

    prompt = f"""You are an expert technical writer specializing in GitHub README files. Generate a comprehensive, professional README.md for the following project.

TONE INSTRUCTION: {tone_text}{template_hint}{tags_instruction}

PROJECT INFORMATION:
{project_info}

REQUIRED README SECTIONS (include all that are relevant):
1. Project title with a one-line tagline
2. Shields.io badges (build status, license, language, stars)
3. Table of Contents (auto-linked)
4. About/Description (what this project does and why)
5. Features list (bullet points)
6. Tech Stack / Technologies Used
7. Prerequisites
8. Installation & Setup (step-by-step)
9. Usage / Quick Start
10. Folder Structure (tree format)
11. API Endpoints (if detected, in table format)
12. Environment Variables (table format: Variable | Description | Required)
13. Screenshots section (placeholder with [Screenshot] markers)
14. Contributing Guidelines
15. License
16. Acknowledgements (if applicable)

FORMATTING RULES:
- Use proper Markdown syntax throughout
- Use code blocks with language hints (```bash, ```json, etc.)
- Use tables where appropriate (API endpoints, env vars)
- Make the README ready to copy-paste directly to GitHub
- Start with # ProjectName and end cleanly

Generate the complete README now:"""

    return prompt


def build_analysis_prompt(file_contents: str) -> str:
    return f"""Analyze the following project files and extract structured information. Return ONLY a valid JSON object with no extra text.

Files:
{file_contents[:8000]}

Return this exact JSON structure:
{{
  "name": "project name from package.json or folder name",
  "description": "brief project description",
  "languages": ["list of programming languages detected"],
  "frameworks": ["list of frameworks like React, Express, Django, etc."],
  "databases": ["list of databases like MongoDB, PostgreSQL, etc."],
  "project_type": "frontend|backend|fullstack|library|cli|mobile|ml",
  "dependencies": ["top 15 dependency names"],
  "has_docker": true or false,
  "has_cicd": true or false,
  "api_endpoints": ["list of detected API route patterns"],
  "env_vars": ["list of environment variable names from .env.example or config files"]
}}"""
