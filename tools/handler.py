import json

from datetime import datetime
from dataclasses import dataclass
from functools import wraps

from .image_processor import ImageProcessor


@dataclass
class ServerConfig:
    host: str
    port: int
    max_size: int

    @classmethod
    def from_json(cls, config_path: str):
        with open(config_path) as f:
            config = json.load(f)["websocket"]
        return cls(
            host=config["host"],
            port=config["port"],
            max_size=config["max_size"]
        )


class HandlerFactory:
    def __init__(self, processor: ImageProcessor):
        self.processor = processor

    def create_handler(self):
        async def handler(websocket):
            async for message in websocket:
                if isinstance(message, bytes) and len(message) >= 4:
                    color = (int(message[0]), int(message[1]), int(message[2]))
                    image_data = message[3:]
                    processed = self.processor.process_image(image_data, color)
                    await websocket.send(processed)

        return handler


def log_websocket_connections(func):
    @wraps(func)
    async def wrapper(websocket, *args, **kwargs):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{now}] [Connected] {websocket.remote_address}")
        try:
            return await func(websocket, *args, **kwargs)
        finally:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{now}] [Disconnected] {websocket.remote_address}")

    return wrapper
