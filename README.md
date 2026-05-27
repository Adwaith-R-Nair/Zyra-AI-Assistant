# ZYRA : Intelligent Voice Assistant

A Jarvis-class voice agent built on ESP32-S3 with a Python laptop server backend.

## Architecture

ESP32-S3 (edge) ←→ WebSocket ←→ Laptop Server (brain)

ESP32-S3 handles wake word detection, audio capture, and playback.
Laptop server handles STT, LLM, TTS, and memory.

## Hardware

- ESP32-S3 N16R8 (16MB Flash, 8MB PSRAM)
- INMP441 I2S Microphone
- MAX98357A I2S Amplifier
- SSD1306 0.96" OLED Display (I2C)
- WS2812B RGB LEDs x5
- Tactile button

## Server Stack

| Component | Technology |
|-----------|-----------|
| STT | faster-whisper (medium.en) |
| LLM | Ollama (llama3.2:3b) |
| TTS | Piper TTS |
| Memory | ChromaDB + SQLite |
| Server | FastAPI + WebSocket |

## Setup

### Requirements
- Python 3.11
- NVIDIA GPU with CUDA (recommended)
- Ollama installed

### Installation

```bash
# Clone the repo
git clone https://github.com/yourusername/zyra-server.git
cd zyra-server

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Pull Ollama model
ollama pull llama3.2:3b

# Download Piper voice model
# Place en_US-lessac-high.onnx and .onnx.json in models/
# Download from: https://huggingface.co/rhasspy/piper-voices

# Run component tests
python test_components.py

# Start server
python main.py
```

### Configuration
Copy `.env.example` to `.env` and fill in your values.

## Pin Configuration

| Component | Pin | GPIO |
|-----------|-----|------|
| INMP441 SCK | I2S Clock | GPIO 1 |
| INMP441 WS | I2S Word Select | GPIO 2 |
| INMP441 SD | I2S Data | GPIO 3 |
| INMP441 L/R | Channel Select | GND |
| MAX98357 BCLK | I2S Clock | GPIO 4 |
| MAX98357 LRC | I2S Word Select | GPIO 5 |
| MAX98357 DIN | I2S Data | GPIO 21 |
| SSD1306 SDA | I2C Data | GPIO 8 |
| SSD1306 SCL | I2C Clock | GPIO 9 |
| WS2812B DIN | LED Data | GPIO 13 |
| Button | Input | GPIO 48 |