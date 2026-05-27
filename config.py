import os
from dotenv import load_dotenv

load_dotenv()

os.environ["ANONYMIZED_TELEMETRY"] = "False"
os.environ["CHROMA_SERVER_NOFILE"] = "65536"

# ── Server ────────────────────────────────────────
HOST = "0.0.0.0"
PORT = 8765

# ── Ollama ────────────────────────────────────────
OLLAMA_URL = "http://localhost:11434"
OLLAMA_MODEL = "llama3.2:3b"

# ── Whisper ───────────────────────────────────────
WHISPER_MODEL = "medium.en"    # RTX 3060 handles this easily
WHISPER_DEVICE = "cuda"
WHISPER_COMPUTE = "float16"

# ── Piper TTS ─────────────────────────────────────
PIPER_MODEL_PATH = r"C:\zyra-server\models\en_US-lessac-high.onnx"

# ── Audio ─────────────────────────────────────────
SAMPLE_RATE = 16000
CHANNELS = 1
SAMPLE_WIDTH = 2

# ── Memory ────────────────────────────────────────
CHROMA_PATH = r"C:\zyra-server\memory\chromadb"
SQLITE_PATH = r"C:\zyra-server\memory\zyra.db"

# ── ZYRA Personality ──────────────────────────────
SYSTEM_PROMPT = """You are ZYRA, an intelligent voice assistant with a sharp,
confident personality. You are direct, witty, and genuinely helpful.
You speak in concise sentences optimized for voice — no markdown,
no bullet points, no lists. Just clean spoken language.
You have a slightly futuristic tone — calm but with personality.
Never say you are an AI or mention Claude, Ollama, or any underlying model.
You are simply ZYRA.
When you don't know something, say so directly.
Keep responses under 3 sentences unless the question genuinely requires more.
Current conversation context will be provided to you."""
