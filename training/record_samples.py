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

SAMPLE_RATE   = 16000
CHANNELS      = 1
CHUNK         = 1024
RECORD_SECS   = 2       # each sample is 2 seconds
OUTPUT_DIR    = r"C:\zyra-server\training\samples\positive"
TARGET_COUNT  = 100     # record 100 samples

os.makedirs(OUTPUT_DIR, exist_ok=True)

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
    # Count existing samples
    existing = [f for f in os.listdir(OUTPUT_DIR)
                if f.endswith(".wav")]
    start    = len(existing)

    print(f"Recording 'Hey Zyra' training samples")
    print(f"Already have: {start} samples")
    print(f"Target: {TARGET_COUNT} samples")
    print("─────────────────────────────────────")
    print("Tips for good samples:")
    print("  - Say it naturally, not robotically")
    print("  - Vary your distance (30cm to 1m)")
    print("  - Vary your volume slightly")
    print("  - Record in your actual room")
    print("  - Try different times of day")
    print("─────────────────────────────────────")

    for i in range(start, TARGET_COUNT):
        filename = os.path.join(
            OUTPUT_DIR, f"hey_zyra_{i:03d}.wav"
        )

        print(f"\nSample {i+1}/{TARGET_COUNT}")
        print("Get ready... (press Enter when ready)")
        input()
        print("Recording — say 'Hey Zyra' NOW...")

        record_sample(filename)
        print(f"Saved: {filename}")

        # Short pause between samples
        time.sleep(0.5)

    print(f"\nDone! Recorded {TARGET_COUNT} samples")
    print(f"Saved to: {OUTPUT_DIR}")

if __name__ == "__main__":
    main()