"""
ModelSelector: lists and switches between locally available Ollama models.
"""

import requests


RECOMMENDED_MODELS = [
    {"name": "codellama", "description": "Best for code completion (Meta)", "size": "3.8GB"},
    {"name": "deepseek-coder", "description": "Excellent for Python/JS", "size": "1.3GB"},
    {"name": "mistral", "description": "Fast general purpose", "size": "4.1GB"},
    {"name": "llama3", "description": "Strong reasoning", "size": "4.7GB"},
    {"name": "phi3", "description": "Lightweight, fast", "size": "2.3GB"},
]


class ModelSelector:
    def __init__(self, config: dict):
        self.ollama_url = config.get("ollama_url", "http://localhost:11434")
        self.current_model = config.get("model", "codellama")

    def list_models(self) -> dict:
        """List all locally available Ollama models."""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            data = response.json()
            local_models = [m["name"] for m in data.get("models", [])]

            return {
                "current": self.current_model,
                "local": local_models,
                "recommended": RECOMMENDED_MODELS,
            }

        except requests.exceptions.ConnectionError:
            return {
                "current": self.current_model,
                "local": [],
                "recommended": RECOMMENDED_MODELS,
                "error": "Ollama not running. Start with: ollama serve",
            }
        except Exception as e:
            return {"error": str(e)}

    def set_model(self, model: str):
        """Switch the active model."""
        self.current_model = model
        print(f"[ACE-Codex] Switched to model: {model}")

    def pull_model(self, model: str) -> bool:
        """Pull a model from Ollama registry."""
        try:
            print(f"[ACE-Codex] Pulling model: {model} (this may take a while)...")
            response = requests.post(
                f"{self.ollama_url}/api/pull",
                json={"name": model},
                timeout=300,
                stream=True,
            )
            for line in response.iter_lines():
                if line:
                    import json
                    data = json.loads(line)
                    if "status" in data:
                        print(f"  {data['status']}")
            print(f"[ACE-Codex] Model {model} ready.")
            return True
        except Exception as e:
            print(f"[ACE-Codex] Pull failed: {e}")
            return False
