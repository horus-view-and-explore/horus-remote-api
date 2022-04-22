from contextlib import contextmanager

import pytest

from horus_remote_api.client import Client
from horus_remote_api.connection_socketio import SocketIOConnection

from .server import socketio_server_context


@contextmanager
def client_context(url):
    conn = SocketIOConnection(url, None)
    with Client(conn) as client:
        yield client


def test_ping():
    async def handler(emit, sid, data):
        await emit(
            "ctrl",
            {
                "Request": data["Request"],
                "Response": {
                    "ResponseTo": data["Request"]["Id"],
                    "Type": data["Request"]["Type"],
                },
            },
        )

    with socketio_server_context({"send-ctrl": handler}) as server_url:
        with client_context(server_url) as client:
            assert client.ping() == {}


def test_timeout():
    async def handler(emit, sid, data):
        pass

    with socketio_server_context({"send-ctrl": handler}) as server_url:
        with client_context(server_url) as client:
            with pytest.raises(TimeoutError):
                client.ping(timeout=1.0)
