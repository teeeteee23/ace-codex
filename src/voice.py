"""
WhisperVoiceEngine: transcribes audio to code using OpenAI Whisper locally.
Supports CUDA acceleration on compatible GPUs.
"""

import os


class WhisperVoiceEngine:
    def __init__(self, config: dict):
        self.enabled = config.get("voice_enabled", True)
        self.model_size = config.get("whisper_model", "base")
        self.device = config.get("whisper_device", "cuda")
        self._model = None

    def _load_model(self):
        """Lazy-load Whisper model on first use."""
        if self._model is None:
            try:
                import whisper
                print(f"[ACE-Codex Voice] Loading Whisper {self.model_size} on {self.device}...")
                self._model = whisper.load_model(self.model_size, device=self.device)
                print("[ACE-Codex Voice] Whisper ready.")
            except ImportError:
                print("[ACE-Codex Voice] Whisper not installed. Run: pip install openai-whisper")
            except Exception as e:
                print(f"[ACE-Codex Voice] Failed to load Whisper: {e}")

    def transcribe(self, audio_path: str, language: str = None) -> str:
        """
        Transcribe an audio file to text.
        audio_path: path to .wav or .mp3 file
        language: optional ISO language code (e.g. 'en', 'ur')
        """
        if not self.enabled:
            return ""

        if not os.path.exists(audio_path):
            return ""

        self._load_model()
        if self._model is None:
            return ""

        try:
            options = {}
            if language:
                options["language"] = language

            result = self._model.transcribe(audio_path, **options)
            text = result.get("text", "").strip()
            print(f"[ACE-Codex Voice] Transcribed: {text[:80]}...")
            return text

        except Exception as e:
            print(f"[ACE-Codex Voice] Transcription error: {e}")
            return ""

    def record_and_transcribe(self, duration: int = 5, language: str = "en") -> str:
        """
        Record audio from microphone and transcribe it.
        Requires: pip install sounddevice scipy
        """
        try:
            import sounddevice as sd
            import scipy.io.wavfile as wav
            import tempfile
            import numpy as np

            print(f"[ACE-Codex Voice] Recording for {duration}s...")
            sample_rate = 16000
            recording = sd.rec(
                int(duration * sample_rate),
                samplerate=sample_rate,
                channels=1,
                dtype="int16",
            )
            sd.wait()

            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                wav.write(f.name, sample_rate, recording)
                return self.transcribe(f.name, language=language)

        except ImportError:
            print("[ACE-Codex Voice] Install sounddevice and scipy for mic recording.")
            return ""
        except Exception as e:
            print(f"[ACE-Codex Voice] Recording error: {e}")
            return ""
