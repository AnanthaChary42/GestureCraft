import os
import urllib.request
import subprocess
import sys

MODEL_URL = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
MODEL_DIR = os.path.join("backend", "models")
MODEL_PATH = os.path.join(MODEL_DIR, "hand_landmarker.task")

def install_requirements():
    print("Installing Python dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("Dependencies installed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {e}")
        sys.exit(1)

def download_model():
    if os.path.exists(MODEL_PATH):
        print(f"Model already exists at {MODEL_PATH}")
        return

    print(f"Creating directory {MODEL_DIR}...")
    os.makedirs(MODEL_DIR, exist_ok=True)

    print(f"Downloading model from {MODEL_URL}...")
    try:
        urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
        print("Model downloaded successfully.")
    except Exception as e:
        print(f"Failed to download model: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("Starting setup...")
    install_requirements()
    download_model()
    print("Setup complete! You can now run the application.")
