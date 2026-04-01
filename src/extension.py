"""
ACE-Codex: AI-powered VS Code extension using local Ollama models.
Free, private GitHub Copilot alternative.
"""

import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from src.completion import CompletionEngine
from src.rag import RAGProcessor
from src.voice import WhisperVoiceEngine
from src.model_selector import ModelSelector

# Default config
DEFAULT_CONFIG = {
    "host": "localhost",
    "port": 5005,
    "model": "codellama",
    "ollama_url": "http://localhost:11434",
    "rag_enabled": True,
    "voice_enabled": True,
    "max_tokens": 150,
    "temperature": 0.2,
}


class ACECodexHandler(BaseHTTPRequestHandler):
    """HTTP handler for VS Code extension communication."""

    engine: CompletionEngine = None
    rag: RAGProcessor = None
    voice: WhisperVoiceEngine = None
    selector: ModelSelector = None

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        data = json.loads(body)

        if self.path == "/complete":
            result = self.engine.complete(
                prefix=data.get("prefix", ""),
                suffix=data.get("suffix", ""),
                language=data.get("language", "python"),
                context=data.get("context", ""),
            )
            self._respond({"completion": result})

        elif self.path == "/rag/index":
            self.rag.index_directory(data.get("path", "."))
            self._respond({"status": "indexed"})

        elif self.path == "/rag/query":
            result = self.rag.query(data.get("text", ""))
            self._respond({"context": result})

        elif self.path == "/voice/transcribe":
            result = self.voice.transcribe(data.get("audio_path", ""))
            self._respond({"text": result})

        elif self.path == "/models/list":
            models = self.selector.list_models()
            self._respond({"models": models})

        elif self.path == "/models/select":
            self.selector.set_model(data.get("model", "codellama"))
            self.engine.set_model(data.get("model", "codellama"))
            self._respond({"status": "ok"})

        else:
            self._respond({"error": "Unknown endpoint"}, 404)

    def _respond(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def log_message(self, format, *args):
        pass  # Silence default logging


def start_server(config=None):
    cfg = {**DEFAULT_CONFIG, **(config or {})}

    # Initialize components
    ACECodexHandler.engine = CompletionEngine(cfg)
    ACECodexHandler.rag = RAGProcessor(cfg)
    ACECodexHandler.voice = WhisperVoiceEngine(cfg)
    ACECodexHandler.selector = ModelSelector(cfg)

    server = HTTPServer((cfg["host"], cfg["port"]), ACECodexHandler)
    print(f"[ACE-Codex] Server running at http://{cfg['host']}:{cfg['port']}")
    print(f"[ACE-Codex] Model: {cfg['model']} | RAG: {cfg['rag_enabled']} | Voice: {cfg['voice_enabled']}")

    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server


if __name__ == "__main__":
    server = start_server()
    try:
        input("[ACE-Codex] Press Enter to stop...\n")
    except KeyboardInterrupt:
        pass
    server.shutdown()
    print("[ACE-Codex] Stopped.")
