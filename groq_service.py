import os
from groq import Groq

GROQ_MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "mixtral-8x7b-32768",
    "gemma2-9b-it"
]


def generate_with_groq(prompt: str, model: str = "llama-3.3-70b-versatile", api_key: str = None) -> str:
    key = api_key or os.getenv("GROQ_API_KEY")
    if not key:
        raise Exception("Groq API key not provided. Set GROQ_API_KEY environment variable or provide it in the request.")

    client = Groq(api_key=key)

    try:
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert technical writer. Generate professional, well-structured README.md files in valid Markdown format."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=4096,
            top_p=0.9
        )
        return completion.choices[0].message.content
    except Exception as e:
        err = str(e)
        if "api_key" in err.lower() or "authentication" in err.lower():
            raise Exception("Invalid Groq API key. Please check your key and try again.")
        elif "rate_limit" in err.lower():
            raise Exception("Groq rate limit reached. Please wait a moment and try again.")
        elif "model" in err.lower():
            raise Exception(f"Model '{model}' not available on Groq. Try a different model.")
        raise Exception(f"Groq error: {err}")


def get_groq_models() -> list:
    return GROQ_MODELS
