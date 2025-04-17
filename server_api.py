import asyncio

from aiohttp import web
from aiortc.contrib.media import MediaRelay

from tools.image_processor import ImageProcessor, PyAVframeIo
from tools.handler import HandlerFactory, ServerConfig

pcs = set()
relay = MediaRelay()


async def on_shutdown(app):
    await asyncio.gather(*[pc.close() for pc in pcs])
    pcs.clear()


async def main():
    config = ServerConfig.from_json("config.json")
    processor = ImageProcessor(PyAVframeIo())
    handler = HandlerFactory(processor, pcs, relay).create_handler()

    app = web.Application()
    app.on_shutdown.append(on_shutdown)
    app.router.add_get(config.ws_path, handler)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, config.host, config.port)
    await site.start()

    print(f"Ready for signaling on ws://{config.host}:{config.port}")
    await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
