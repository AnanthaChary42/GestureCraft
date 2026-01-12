# GestureCraft: Hand-Controlled Hologram Builder ✋✨🧱

**GestureCraft** is an interactive AR-like application that allows you to create and manipulate 3D holographic blocks using simple hand gestures. Built with Python (MediaPipe, OpenCV) and JavaScript (Three.js), it creates a seamless bridge between computer vision and 3D rendering.

![Demo](frontend/trash_bin.png) <!-- Placeholder for a real demo screenshot -->

## 🌟 Features

*   **Hand Tracking**: Real-time hand landmark detection using MediaPipe.
*   **Touchless Interface**: Control the 3D scene entirely with your index finger.
*   **Gesture Recognition**:
    *   👌 **Pinch**: Create a new block or Grab an existing one.
    *   🖐 **Release**: Drop the block.
*   **Intuitive Building**:
    *   **Spawn**: Pinch in empty space to create a block.
    *   **Move**: Pinch and drag to move blocks.
    *   **Color**: Hover over the **palette spheres** to change your "brush" color, which applies to new blocks.
    *   **Delete**: Drag a block to the **Trash Bin** icon to delete it.
*   **Visual Feedback**:
    *   Blocks change opacity when grabbed.
    *   "Deleting Block" warning text and red tint when near the bin.
    *   Live video background for an Augmented Reality feel.

## 🛠️ Architecture

*   **Backend (Python)**:
    *   Captures webcam feed.
    *   Tracks hand landmarks using `mediapipe.tasks`.
    *   Detects gestures (Pinch vs Open Palm).
    *   Streams video frames (Base64) and hand data (JSON) via WebSockets.
*   **Frontend (HTML/JS)**:
    *   Renders the 3D scene using **Three.js**.
    *   Displays the live video feed as a background.
    *   Updates the 3D scene based on real-time WebSocket data.

## 🚀 Installation & Setup

### Prerequisites
*   Python 3.8 - 3.11
*   A webcam

### 1. clone the repository
```bash
git clone https://github.com/AnanthaChary42/GestureCraft.git
cd GestureCraft
```

### 2. Install Dependencies
We have provided a setup script to automate the installation of Python packages and the necessary ML models.

```bash
python setup_project.py
```
*Allows the script to install `opencv-python`, `mediapipe`, `websockets`, `numpy` and download the `hand_landmarker.task` model.*

## 🕹️ Usage

1.  **Start the Backend**:
    This will start the WebSocket server and the video processing loop.
    ```bash
    python backend/main.py
    ```

2.  **Open the Frontend**:
    Open `frontend/index.html` in your web browser.
    *   *Note: For the best experience, you may need to run a local server (e.g., Live Server in VS Code or `python -m http.server`) to serve the frontend, though simple file access often works.*

3.  **Start Building!**
    *   Show your hand to the camera.
    *   **Pinch** your thumb and index finger to create a block.
    *   **Move** it around.
    *   **Drop** it by releasing the pinch.
    *   **Color** it by hovering over the colored spheres at the bottom.
    *   **Trash** it by dragging it to the bin icon.

## 📁 Project Structure

```
Hologram/
├── backend/            # Python source code
│   ├── tracking/       # Hand tracking & MediaPipe logic
│   ├── gestures/       # Gesture detection (Pinch, etc.)
│   ├── communication/  # WebSocket server
│   ├── camera/         # Webcam capture
│   └── main.py         # Entry point
├── frontend/           # Web interface
│   ├── app.js          # Three.js & Game Logic
│   ├── index.html      # Main page
│   └── style.css       # Styling
├── setup_project.py    # Auto-dependency installer
└── requirements.txt    # Python packages
```

## 🤝 Contributing
Contributions are welcome! Feel free to open issues or submit pull requests.

## 📄 License
MIT License
