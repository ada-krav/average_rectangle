import asyncio
import websockets

from tools.image_processor import ImageProcessor
from tools.handler import ServerConfig, HandlerFactory, log_websocket_connections


async def main():
    config = ServerConfig.from_json("config.json")

    processor = ImageProcessor()
    handler = HandlerFactory(processor).create_handler()

    async with websockets.serve(
        log_websocket_connections(handler), config.host, config.port, max_size=config.max_size
    ):
        print(f"Server started on ws://{config.host}:{config.port}")
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
