import sys
import os

if sys.platform == "win32":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")
    os.environ["PYTHONIOENCODING"] = "utf-8"

import pyaudio
import wave
import time

SAMPLE_RATE  = 16000
CHANNELS     = 1
CHUNK        = 1024
RECORD_SECS  = 2
OUTPUT_DIR   = r"C:\zyra-server\training\samples\negative"
TARGET_COUNT = 100

os.makedirs(OUTPUT_DIR, exist_ok=True)

PROMPTS = [
    "Say: 'What time is it'",
    "Say: 'Turn on the lights'",
    "Say: 'Play some music'",
    "Say: 'Hey there'",
    "Say: 'Good morning'",
    "Say: 'How are you doing'",
    "Say: 'Tell me a joke'",
    "Say: 'What is the weather'",
    "Say: 'Set a timer'",
    "Say: 'Hey Google'",
    "Say: 'Alexa stop'",
    "Say: 'OK computer'",
    "Say: 'Hello there'",
    "Say: 'What day is today'",
    "Say: 'Open the door'",
    "Say: 'Hey Siri'",
    "Say: 'Turn off the fan'",
    "Say: 'Call mom'",
    "Say: 'Send a message'",
    "Say: 'Hey Zara'",         # close to Hey Zyra
    "Say: 'Hey Zira'",         # close to Hey Zyra
    "Say: 'Hey Sierra'",       # close to Hey Zyra
    "Say anything randomly",
    "Cough or clear throat",
    "Say some numbers: 1 2 3",
]

def record_sample(filename: str):
    pa     = pyaudio.PyAudio()
    stream = pa.open(
        format            = pyaudio.paInt16,
        channels          = CHANNELS,
        rate              = SAMPLE_RATE,
        input             = True,
        frames_per_buffer = CHUNK
    )

    frames = []
    for _ in range(int(SAMPLE_RATE / CHUNK * RECORD_SECS)):
        frames.append(stream.read(CHUNK,
                      exception_on_overflow=False))

    stream.stop_stream()
    stream.close()
    pa.terminate()

    with wave.open(filename, "wb") as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(b"".join(frames))

def main():
    existing = [f for f in os.listdir(OUTPUT_DIR)
                if f.endswith(".wav")]
    start    = len(existing)

    print(f"Recording negative samples")
    print(f"Already have: {start} samples")
    print(f"Target: {TARGET_COUNT} samples")
    print("─────────────────────────────────────")
    print("These are things that should NOT")
    print("trigger the wake word.")
    print("─────────────────────────────────────")

    for i in range(start, TARGET_COUNT):
        filename = os.path.join(
            OUTPUT_DIR, f"negative_{i:03d}.wav"
        )
        prompt = PROMPTS[i % len(PROMPTS)]

        print(f"\nSample {i+1}/{TARGET_COUNT}")
        print(f"Prompt: {prompt}")
        print("Press Enter when ready...")
        input()
        print("Recording NOW...")

        record_sample(filename)
        print(f"Saved: {filename}")
        time.sleep(0.3)

    print(f"\nDone! {TARGET_COUNT} negative samples recorded")

if __name__ == "__main__":
    main()