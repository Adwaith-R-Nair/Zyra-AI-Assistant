import sys
import os

if sys.platform == "win32":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")
    os.environ["PYTHONIOENCODING"] = "utf-8"

import pyaudio
import numpy as np
from openwakeword.model import Model

MODEL_PATH  = r"C:\zyra-server\models\hey_zyra.onnx"
THRESHOLD   = 0.5      # detection confidence threshold
SAMPLE_RATE = 16000
CHUNK       = 1280     # openWakeWord needs 80ms chunks

def main():
    print("Loading Hey Zyra model...")
    oww = Model(
        wakeword_models=[MODEL_PATH],
        inference_framework="onnx"
    )

    pa     = pyaudio.PyAudio()
    stream = pa.open(
        format            = pyaudio.paInt16,
        channels          = 1,
        rate              = SAMPLE_RATE,
        input             = True,
        frames_per_buffer = CHUNK
    )

    print("Listening for 'Hey Zyra'...")
    print("Press Ctrl+C to stop")
    print("─────────────────────────")

    try:
        while True:
            audio  = stream.read(
                       CHUNK,
                       exception_on_overflow=False
                     )
            audio  = np.frombuffer(audio, dtype=np.int16)

            prediction = oww.predict(audio)

            for name, score in prediction.items():
                if score > THRESHOLD:
                    print(f">>> HEY ZYRA DETECTED "
                          f"(confidence: {score:.3f})")
                elif score > 0.2:
                    # Show near-misses for calibration
                    print(f"    Near miss: {score:.3f}")

    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        stream.stop_stream()
        stream.close()
        pa.terminate()

if __name__ == "__main__":
    main()