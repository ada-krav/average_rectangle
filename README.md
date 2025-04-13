# Webcam Stream with Average Rectangle

## Description

This project captures video from the client's webcam, adds an average-colored rectangle to the center of each frame, and sends it back to the client.

## Requirements

- Python 3.x
- Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

## Running the Backend (Python)

1. Run the WebSocket server:

    ```bash
    python server_api.py
    ```
    or
    ```bash
    python3 server_api.py
    ```



## Running the Frontend

1. Open `index.html` in a web browser (make sure the backend is running).
2. Allow use of your camera (if prompted).

## WebSocket Communication

- The frontend captures webcam frames every 100ms, calculates average pixel color and sends both frame and color to the backend via WebSocket.
- The backend processes the frames and sends them back with an average-colored rectangle drawn in the center.
