import asyncio
import json
import logging
import threading
import time
from contextlib import contextmanager
from functools import partial
from typing import Any, Optional, Dict

import socketio
from aiohttp import web


class SocketioServer:
    def __init__(
        self,
        impl: Dict[str, Any],
        host: Optional[str] = None,
        port: Optional[int] = None,
    ):
        self.host = host or "127.0.0.1"
        self.port = port or 3305

        self._log = logging.getLogger(repr(self))
        self._sio = socketio.AsyncServer(async_mode="aiohttp")
        self._app = web.Application()
        self._sio.attach(self._app)
        self._site = None

        for k, v in impl.items():
            self.register_event_handler(k, v)

        self._log.debug("initialized")

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.host}:{self.port}>"

    async def listen(self):
        runner = web.AppRunner(self._app)
        await runner.setup()
        self._site = web.TCPSite(runner, self.host, self.port)
        await self._site.start()
        self._log.debug("listening")

    async def stop(self):
        if self._site is None:
            raise RuntimeError("server is not running")
        self._log.debug("server stopping")
        await self._site.stop()
        self._log.debug("server stopped")
        self._site = None

    def register_event_handler(self, event, func):
        async def wrapper(emit, sid, data):
            data = json.loads(data)
            result = await func(emit, sid, data)
            return result

        self._sio.on(event)(partial(wrapper, self._sio.emit))
        self._log.debug(f"registered {event=} {func=}")

    @property
    def url(self):
        return f"http://{self.host}:{self.port}"


class SocketioServerThread(threading.Thread):
    _STOP_TIMEOUT = 10.0

    def __init__(self, impl, host=None, port=None):
        self._loop = None
        self._server = SocketioServer(impl, host, port)
        self._running = None
        self._stopped = threading.Event()

        super().__init__(name="socketio_server_thread")

        self._log = logging.getLogger(repr(self))
        self._log.debug("server thread initialized")

    def __repr__(self):
        return f"<{self.__class__.__name__}: name={self.name}>"

    def run(self):
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        self._running = asyncio.Event()

        async def main():
            await self._server.listen()
            await self._running.wait()
            await self._server.stop()
            self._loop.stop()

        self._log.debug("server thread serving")
        self._loop.run_until_complete(main())
        self._log.debug("server thread done")

        self._loop.close()
        self._stopped.set()
        self._loop = None

        self._log.debug("server thread cleaned up")

    def stop(self):
        if self._loop is None:
            raise RuntimeError("server is not running")

        self._loop.call_soon_threadsafe(self._running.set)
        self._stopped.wait(self._STOP_TIMEOUT)

    @property
    def url(self):
        return self._server.url


@contextmanager
def socketio_server_context(impl, host=None, port=None):
    srv = SocketioServerThread(impl, host, port)
    try:
        srv.start()
        # Wait for a bit until the server has started.
        for _ in range(10):
            time.sleep(0.1)
        yield srv.url
    finally:
        srv.stop()
