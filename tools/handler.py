import json
from dataclasses import dataclass

from aiohttp import web, WSMsgType
from aiortc import RTCPeerConnection, RTCSessionDescription, MediaStreamTrack
from aiortc.contrib.media import MediaRelay

from tools.image_processor import ImageProcessor


@dataclass
class ServerConfig:
    host: str
    port: int
    ws_path: str

    @classmethod
    def from_json(cls, config_path: str = "config.json"):
        with open(config_path, "r") as f:
            config = json.load(f).get("websocket", {})
        return cls(
            host=config.get("host"),
            port=config.get("port"),
            ws_path=config.get("ws_path"),
        )


class VideoTransformTrack(MediaStreamTrack):
    kind = "video"

    def __init__(self, track, processor: ImageProcessor, get_color_callback):
        super().__init__()
        self.track = track
        self.processor = processor
        self.get_color = get_color_callback

    async def recv(self):
        frame = await self.track.recv()
        avg_color = self.get_color()
        new_frame = self.processor.process_image(frame, avg_color)
        new_frame.pts = frame.pts
        new_frame.time_base = frame.time_base
        return new_frame


class HandlerFactory:
    def __init__(self, processor: ImageProcessor, pcs: set, relay: MediaRelay):
        self.processor = processor
        self.pcs = pcs
        self.relay = relay

    def create_handler(self):
        async def handler(request):
            ws = web.WebSocketResponse()
            await ws.prepare(request)

            pc = RTCPeerConnection()
            self.pcs.add(pc)
            request.app["pcs"] = self.pcs

            color = {"value": None}

            def get_color():
                return color.get("value", None)

            @pc.on("datachannel")
            def on_datachannel(channel):
                @channel.on("message")
                def on_message(message):
                    try:
                        color["value"] = tuple(message)
                    except Exception as e:
                        print(f"Failed to decode color message: {e}")

            @pc.on("track")
            def on_track(track):
                if track.kind == "video":
                    local_video = VideoTransformTrack(
                        self.relay.subscribe(track), self.processor, get_color
                    )
                    pc.addTrack(local_video)

            try:
                async for msg in ws:
                    if msg.type == WSMsgType.TEXT:
                        data = json.loads(msg.data)
                        if data.get("type") == "offer":
                            offer = RTCSessionDescription(sdp=data["sdp"], type="offer")
                            await pc.setRemoteDescription(offer)
                            answer = await pc.createAnswer()
                            await pc.setLocalDescription(answer)

                            await ws.send_json(
                                {
                                    "type": pc.localDescription.type,
                                    "sdp": pc.localDescription.sdp,
                                }
                            )
            finally:
                await pc.close()
                self.pcs.discard(pc)

            return ws

        return handler
