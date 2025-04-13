const video = document.getElementById("video");
const canvas = document.getElementById("processedCanvas");
const ctx = canvas.getContext("2d", { willReadFrequently: true });

const tempCanvas = document.createElement("canvas");
const tempCtx = tempCanvas.getContext("2d", { willReadFrequently: true });

let socket;
let reconnectTimeout = null;

function connectWebSocket() {
    socket = new WebSocket("ws://localhost:8000");

    socket.onopen = () => {
        console.log("WebSocket connected");
    };

    socket.onclose = () => {
        console.warn("WebSocket closed, retrying in 3s");
        reconnectTimeout = setTimeout(connectWebSocket, 3000);
    };

    socket.onerror = (err) => {
        console.error("WebSocket error:", err);
        socket.close();
    };

    socket.onmessage = event => {
        const img = new Image();
        img.src = URL.createObjectURL(event.data);
        img.onload = () => {
            canvas.width = img.width;
            canvas.height = img.height;
            ctx.drawImage(img, 0, 0);
        };
    };
}

connectWebSocket();

navigator.mediaDevices.getUserMedia({ video: true }).then(stream => {
    video.srcObject = stream;

    const sendFrame = () => {
        if (!socket || socket.readyState !== WebSocket.OPEN) return;
        if (video.videoWidth === 0 || video.videoHeight === 0) return;

        tempCanvas.width = video.videoWidth;
        tempCanvas.height = video.videoHeight;
        tempCtx.drawImage(video, 0, 0);

        const avgColor = getAverageColorFromCanvas(tempCanvas);

        tempCanvas.toBlob(blob => {
            const colorBytes = new Uint8Array([avgColor.r, avgColor.g, avgColor.b]);

            const reader = new FileReader();
            reader.onload = () => {
                const imageBytes = new Uint8Array(reader.result);
                const combined = new Uint8Array(3 + imageBytes.length);
                combined.set(colorBytes, 0);
                combined.set(imageBytes, 3);
                socket.send(combined);
            };
            reader.readAsArrayBuffer(blob);
        }, "image/jpeg");
    };

    setInterval(sendFrame, 100); // frequency in ms
});

function getAverageColorFromCanvas(canvas) {
    const ctx = canvas.getContext("2d");
    const { width, height } = canvas;
    const imageData = ctx.getImageData(0, 0, width, height);
    const data = imageData.data;

    let r = 0, g = 0, b = 0;
    const totalPixels = width * height;

    for (let i = 0; i < data.length; i += 4) {
        r += data[i];
        g += data[i + 1];
        b += data[i + 2];
    }

    return {
        r: Math.round(r / totalPixels),
        g: Math.round(g / totalPixels),
        b: Math.round(b / totalPixels)
    };
}
