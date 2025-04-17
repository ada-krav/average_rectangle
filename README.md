# Webcam Stream with Average Rectangle

## Description

This project captures video from the client's webcam, adds an average-colored rectangle to the center of each frame, and sends it back to the client.

## Requirements

- Python 3.x
- npm (comes with Node.js)
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

1. Install dependencies and start frontend.

 ```bash
     cd frontend
     npm install
     npm start
 ```

 This should open the app in your browser, usually at <http://localhost:3000>. If it didn't happen, check the terminal, usually, it will contain the details

2. Allow use of your camera (if prompted).

## Communication

- WebSocket is used for signaling
- A WebRTC connection is established with the Python backend
- Video is sent as a separate stream and color has its own Data Channel
- The backend processes the frames and sends them back with an average-colored rectangle drawn in the center.

## Notes

- If you periodically get some number printed in the console (like a single 6), it means that your version of aioice library does not include this [fix](https://github.com/aiortc/aioice/commit/c8180d08a46eef4cb0c41d4ba5dbfb65e34cb6f5).
