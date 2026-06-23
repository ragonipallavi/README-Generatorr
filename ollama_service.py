import requests
import os

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

AVAILABLE_MODELS = ["llama3", "mistral", "deepseek-coder", "llama2", "codellama"]


def get_available_models() -> list:
    try:
        resp = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        if resp.status_code == 200:
            models = resp.json().get("models", [])
            return [m["name"].split(":")[0] for m in models]
    except Exception:
        pass
    return AVAILABLE_MODELS


def generate_with_ollama(prompt: str, model: str = "llama3") -> str:
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.7,
            "top_p": 0.9,
            "num_predict": 4096
        }
    }
    try:
        resp = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json=payload,
            timeout=300
        )
        resp.raise_for_status()
        data = resp.json()
        return data.get("response", "")
    except requests.exceptions.ConnectionError:
        raise Exception("Cannot connect to Ollama. Make sure Ollama is running at " + OLLAMA_BASE_URL)
    except requests.exceptions.Timeout:
        raise Exception("Ollama request timed out. The model might be loading. Try again.")
    except Exception as e:
        raise Exception(f"Ollama error: {str(e)}")


def check_ollama_health() -> dict:
    try:
        resp = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        if resp.status_code == 200:
            models = resp.json().get("models", [])
            return {
                "available": True,
                "models": [m["name"] for m in models],
                "url": OLLAMA_BASE_URL
            }
    except Exception:
        pass
    return {"available": False, "models": [], "url": OLLAMA_BASE_URL}
