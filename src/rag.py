"""
RAG (Retrieval-Augmented Generation) processor.
Indexes your codebase and retrieves relevant snippets to include in completions.
"""

import os
import json
import hashlib
from pathlib import Path
from typing import List, Tuple

SUPPORTED_EXTENSIONS = {
    ".py", ".js", ".ts", ".jsx", ".tsx", ".java",
    ".cpp", ".c", ".h", ".rs", ".go", ".sh", ".md"
}

INDEX_FILE = ".ace_codex_index.json"
CHUNK_SIZE = 50  # lines per chunk


class RAGProcessor:
    def __init__(self, config: dict):
        self.index: List[dict] = []
        self.enabled = config.get("rag_enabled", True)

    def index_directory(self, path: str):
        """Walk a directory and index all supported code files."""
        self.index = []
        root = Path(path)

        for file_path in root.rglob("*"):
            if file_path.suffix not in SUPPORTED_EXTENSIONS:
                continue
            if any(p in file_path.parts for p in ["node_modules", ".git", "__pycache__", "venv"]):
                continue
            try:
                chunks = self._chunk_file(file_path)
                self.index.extend(chunks)
            except Exception:
                continue

        # Save index to disk
        index_path = root / INDEX_FILE
        with open(index_path, "w", encoding="utf-8") as f:
            json.dump(self.index, f)

        print(f"[ACE-Codex RAG] Indexed {len(self.index)} chunks from {path}")

    def load_index(self, path: str):
        """Load a previously saved index."""
        index_path = Path(path) / INDEX_FILE
        if index_path.exists():
            with open(index_path, "r", encoding="utf-8") as f:
                self.index = json.load(f)

    def query(self, text: str, top_k: int = 3) -> str:
        """Find the most relevant code chunks for a given query."""
        if not self.enabled or not self.index:
            return ""

        query_tokens = set(text.lower().split())
        scored: List[Tuple[float, str]] = []

        for chunk in self.index:
            chunk_tokens = set(chunk["content"].lower().split())
            overlap = len(query_tokens & chunk_tokens)
            if overlap > 0:
                score = overlap / (len(query_tokens) + 1)
                scored.append((score, chunk["content"], chunk["file"]))

        scored.sort(key=lambda x: x[0], reverse=True)
        top = scored[:top_k]

        if not top:
            return ""

        parts = []
        for score, content, file in top:
            parts.append(f"# From {file}:\n{content}")

        return "\n\n".join(parts)

    def _chunk_file(self, file_path: Path) -> List[dict]:
        """Split a file into overlapping chunks."""
        lines = file_path.read_text(encoding="utf-8", errors="ignore").splitlines()
        chunks = []

        for i in range(0, len(lines), CHUNK_SIZE // 2):
            chunk_lines = lines[i: i + CHUNK_SIZE]
            content = "\n".join(chunk_lines).strip()
            if len(content) < 20:
                continue
            chunks.append({
                "file": str(file_path),
                "start_line": i,
                "content": content,
                "hash": hashlib.md5(content.encode()).hexdigest(),
            })

        return chunks
