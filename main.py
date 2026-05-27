import asyncio
import logging
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from config import HOST, PORT
from stt import STTEngine
from llm import LLMEngine
from tts import TTSEngine
from memory import MemoryEngine

import sys
import os

# Force UTF-8 encoding on Windows
if sys.platform == "win32":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")
    os.environ["PYTHONIOENCODING"] = "utf-8"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s"
)
logger = logging.getLogger(__name__)

# ── Initialize all engines ────────────────────────
logger.info("Starting ZYRA server...")
stt = STTEngine()
llm = LLMEngine()
tts = TTSEngine()
memory = MemoryEngine()
logger.info("All engines ready")

# ── FastAPI app ───────────────────────────────────
app = FastAPI(title="ZYRA Server")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# ── Per-connection conversation history ───────────
# Each ESP32 connection gets its own context
connections: dict = {}


@app.websocket("/zyra")
async def zyra_websocket(websocket: WebSocket):
    await websocket.accept()
    client_id = id(websocket)
    connections[client_id] = []  # conversation history
    logger.info(f"ESP32 connected — client {client_id}")

    try:
        while True:
            # Receive message from ESP32
            data = await websocket.receive()

            # ── Audio data received ────────────────
            if "bytes" in data:
                audio_bytes = data["bytes"]
                logger.info(f"Received {len(audio_bytes)}"
                            f" bytes of audio")

                # Send status back to ESP32
                await websocket.send_json({
                    "status": "processing",
                    "stage":  "transcribing"
                })

                # STT
                loop = asyncio.get_event_loop()
                transcript = await loop.run_in_executor(
                    None, stt.transcribe, audio_bytes
                )

                if not transcript:
                    await websocket.send_json({
                        "status": "error",
                        "message": "Could not understand audio"
                    })
                    continue

                logger.info(f"Transcript: '{transcript}'")

                # Send transcript back to ESP32
                await websocket.send_json({
                    "status":     "processing",
                    "stage":      "thinking",
                    "transcript": transcript
                })

                # Recall relevant memories
                memories = memory.recall_memory(transcript)
                if memories:
                    memory_context = "Relevant context: " + \
                                     " | ".join(memories)
                    connections[client_id].append({
                        "role":    "system",
                        "content": memory_context
                    })

                # LLM
                history = connections[client_id]
                response = await loop.run_in_executor(
                    None, llm.chat, transcript, history
                )

                # Update conversation history
                connections[client_id].append({
                    "role":    "user",
                    "content": transcript
                })
                connections[client_id].append({
                    "role":    "assistant",
                    "content": response
                })

                # Keep history manageable
                if len(connections[client_id]) > 20:
                    connections[client_id] = \
                        connections[client_id][-20:]

                # Log to memory
                memory.log_conversation("user",      transcript)
                memory.log_conversation("assistant", response)

                # TTS
                await websocket.send_json({
                    "status":   "processing",
                    "stage":    "speaking",
                    "response": response
                })

                audio_response = await loop.run_in_executor(
                    None, tts.synthesize, response
                )

                if audio_response:
                    # Send audio length first so ESP32
                    # knows how much data to expect
                    await websocket.send_json({
                        "status":      "audio_incoming",
                        "audio_bytes": len(audio_response)
                    })
                    # Send raw audio
                    await websocket.send_bytes(audio_response)
                    logger.info("Audio response sent to ESP32")
                else:
                    await websocket.send_json({
                        "status":  "error",
                        "message": "TTS failed"
                    })

            # ── Text command received ──────────────
            elif "text" in data:
                msg = json.loads(data["text"])

                if msg.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})

                elif msg.get("type") == "status":
                    logger.info(f"ESP32 status: {msg}")

    except WebSocketDisconnect:
        logger.info(f"ESP32 disconnected — client {client_id}")
        connections.pop(client_id, None)

    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        connections.pop(client_id, None)

# ── Health check endpoint ─────────────────────────


@app.get("/health")
async def health():
    return {
        "status": "online",
        "model":  llm.model,
        "memory": "connected"
    }

# ── Run server ────────────────────────────────────
if __name__ == "__main__":
    logger.info(f"ZYRA server starting on ws://{HOST}:{PORT}")
    uvicorn.run(
        "main:app",
        host=HOST,
        port=PORT,
        reload=False,
        ws_ping_interval=20,
        ws_ping_timeout=30
    )
