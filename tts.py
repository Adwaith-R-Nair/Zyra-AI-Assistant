import logging
import os
import subprocess
import json

logger = logging.getLogger(__name__)

PIPER_EXE = r"C:\zyra-server\venv\Scripts\piper.exe"
MODEL_PATH = r"C:\zyra-server\models\en_US-lessac-high.onnx"


class TTSEngine:
    def __init__(self):
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(
                f"Piper model not found: {MODEL_PATH}"
            )
        if not os.path.exists(PIPER_EXE):
            raise FileNotFoundError(
                f"piper.exe not found: {PIPER_EXE}"
            )

        # Read config with explicit UTF-8 encoding
        config_path = MODEL_PATH + ".json"
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        self.sample_rate = config["audio"]["sample_rate"]
        logger.info(
            f"TTS engine ready — "
            f"sample rate: {self.sample_rate}Hz"
        )

    def synthesize(self, text: str) -> bytes:
        """
        Takes text string.
        Returns raw 16-bit PCM audio bytes.
        """
        try:
            result = subprocess.run(
                [
                    PIPER_EXE,
                    "--model",            MODEL_PATH,
                    "--output-raw",
                    "--sentence-silence", "0.2"
                ],
                input=text.encode("utf-8"),
                capture_output=True,
                timeout=30,
                env={**os.environ, "PYTHONIOENCODING": "utf-8"}
            )

            if result.returncode != 0:
                error = result.stderr.decode("utf-8", errors="ignore")
                logger.error(f"Piper error: {error}")
                return b""

            audio_bytes = result.stdout

            if len(audio_bytes) == 0:
                # stderr may have info even on success
                stderr_msg = result.stderr.decode(
                    "utf-8", errors="ignore"
                )
                logger.warning(f"Zero bytes. Piper said: {stderr_msg}")
                return b""

            logger.info(
                f"TTS synthesized {len(audio_bytes)} bytes "
                f"for: '{text[:50]}'"
            )
            return audio_bytes

        except subprocess.TimeoutExpired:
            logger.error("TTS timeout")
            return b""
        except Exception as e:
            logger.error(f"TTS error: {e}")
            return b""
