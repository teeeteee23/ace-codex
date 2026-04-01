"""
Completion engine: sends prompts to local Ollama and returns inline completions.
"""

import requests


LANGUAGE_HINTS = {
    "python": "# Python code",
    "javascript": "// JavaScript code",
    "typescript": "// TypeScript code",
    "java": "// Java code",
    "cpp": "// C++ code",
    "rust": "// Rust code",
    "go": "// Go code",
    "bash": "# Bash script",
}


class CompletionEngine:
    def __init__(self, config: dict):
        self.ollama_url = config.get("ollama_url", "http://localhost:11434")
        self.model = config.get("model", "codellama")
        self.max_tokens = config.get("max_tokens", 150)
        self.temperature = config.get("temperature", 0.2)

    def set_model(self, model: str):
        self.model = model

    def complete(self, prefix: str, suffix: str, language: str = "python", context: str = "") -> str:
        """
        Generate inline code completion given the text before and after the cursor.
        """
        lang_hint = LANGUAGE_HINTS.get(language, f"// {language} code")
        rag_block = f"\n\n# Relevant context from your codebase:\n{context}" if context.strip() else ""

        prompt = (
            f"{lang_hint}{rag_block}\n\n"
            f"# Complete the following code. Output ONLY the completion, no explanations.\n\n"
            f"{prefix}<FILL>{suffix}"
        )

        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "num_predict": self.max_tokens,
                        "temperature": self.temperature,
                        "stop": ["\n\n", "```", "#"],
                    },
                },
                timeout=15,
            )
            result = response.json()
            completion = result.get("response", "").strip()
            # Clean up any accidental repetition of the prefix
            if completion.startswith(prefix.strip()):
                completion = completion[len(prefix.strip()):].strip()
            return completion

        except requests.exceptions.ConnectionError:
            return ""  # Ollama not running — fail silently
        except Exception as e:
            print(f"[ACE-Codex] Completion error: {e}")
            return ""
