import React, { useEffect, useRef } from "react";
import { loadConfig } from '../config';


const WebRTCImageProcessing = () => {
    const localVideoRef = useRef(null);
    const remoteVideoRef = useRef(null);
    const pcRef = useRef(null);
    const socketRef = useRef(null);
    const channelRef = useRef(null);
    const canvasRef = useRef(document.createElement("canvas"));

    useEffect(() => {
        const startWebRTC = async () => {
            const config = await loadConfig();
            const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });

            if (localVideoRef.current) {
                localVideoRef.current.srcObject = stream;
            }

            const pc = new RTCPeerConnection();
            pcRef.current = pc;
            stream.getTracks().forEach(track => pc.addTrack(track, stream));

            pc.ontrack = (event) => {
                if (remoteVideoRef.current && remoteVideoRef.current.srcObject !== event.streams[0]) {
                    remoteVideoRef.current.srcObject = event.streams[0];
                }
            };

            // separate DataChannel to send color
            const channel = pc.createDataChannel("color");
            channelRef.current = channel;

            channel.onopen = () => {
                console.log("DataChannel open");
                const video = localVideoRef.current;
                const canvas = canvasRef.current;
                const ctx = canvas.getContext("2d", { willReadFrequently: true });

                function captureAndSend() {
                    if (channel.readyState !== "open") return;
                    if (!video || video.videoWidth === 0 || video.videoHeight === 0) {
                        requestAnimationFrame(captureAndSend);
                        return;
                    }

                    canvas.width = video.videoWidth;
                    canvas.height = video.videoHeight;
                    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

                    const avgColor = getAverageColorFromCanvas(canvas);
                    const colorBytes = new Uint8Array([avgColor.r, avgColor.g, avgColor.b]);

                    try {
                        channel.send(colorBytes);
                    } catch (e) {
                        console.warn("Send error", e);
                    }

                    requestAnimationFrame(captureAndSend);
                }
                captureAndSend();
            };
            // we are using web socket for signaling
            const socket = new WebSocket(`ws://${config.host}:${config.port}${config.ws_path}`);
            socketRef.current = socket;

            socket.onopen = async () => {
                const offer = await pc.createOffer();
                await pc.setLocalDescription(offer);

                socket.send(JSON.stringify({
                    type: "offer",
                    sdp: pc.localDescription.sdp
                }));
            };

            socket.onmessage = async (event) => {
                const data = JSON.parse(event.data);
                if (data.type === "answer") {
                    await pc.setRemoteDescription(new RTCSessionDescription(data));
                }
            };

            socket.onerror = (e) => {
                console.error("WebSocket error", e);
            };
        };

        const getAverageColorFromCanvas = (canvas) => {
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
        };

        startWebRTC();

        // clean up
        return () => {
            if (pcRef.current) {
                pcRef.current.close();
            }
            if (socketRef.current) {
                socketRef.current.close();
            }
        };
    }, []);

    return (
        <div>
            <video
                ref={localVideoRef}
                autoPlay
                playsInline
                style={{ display: 'block', maxWidth: '100%', margin: 'auto' }}
            />
            <video
                ref={remoteVideoRef}
                autoPlay
                playsInline
                style={{ display: 'block', maxWidth: '100%', margin: 'auto' }}
            />
        </div>
    );
};

export default WebRTCImageProcessing;
