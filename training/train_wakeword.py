import sys
import os

if sys.platform == "win32":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")
    os.environ["PYTHONIOENCODING"] = "utf-8"

from openwakeword.train import train_model
import glob

POSITIVE_DIR  = r"C:\zyra-server\training\samples\positive"
NEGATIVE_DIR  = r"C:\zyra-server\training\samples\negative"
OUTPUT_DIR    = r"C:\zyra-server\models"
MODEL_NAME    = "hey_zyra"

def main():
    positive_files = glob.glob(
        os.path.join(POSITIVE_DIR, "*.wav")
    )
    negative_files = glob.glob(
        os.path.join(NEGATIVE_DIR, "*.wav")
    )

    print(f"Positive samples : {len(positive_files)}")
    print(f"Negative samples : {len(negative_files)}")

    if len(positive_files) < 50:
        print("Need at least 50 positive samples")
        print(f"Currently have: {len(positive_files)}")
        return

    print("\nStarting training...")
    print("This takes 5-15 minutes on your RTX 3060")

    train_model(
        model_name          = MODEL_NAME,
        positive_data       = POSITIVE_DIR,
        negative_data       = NEGATIVE_DIR,
        output_dir          = OUTPUT_DIR,
        n_epochs            = 100,
        learning_rate       = 0.001,
        batch_size          = 32,
        val_split           = 0.2,
    )

    model_path = os.path.join(
        OUTPUT_DIR, f"{MODEL_NAME}.onnx"
    )
    if os.path.exists(model_path):
        print(f"\nTraining complete!")
        print(f"Model saved: {model_path}")
    else:
        print("\nTraining may have failed")
        print(f"Check {OUTPUT_DIR} for output files")

if __name__ == "__main__":
    main()