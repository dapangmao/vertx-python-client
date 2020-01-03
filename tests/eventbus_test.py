import logging
import json
import time
import asyncio

import pytest

from vertx import EventBus, Payload

API_VERSION = 1.1
PORT = 8765
HOST = '127.0.0.1'
LOGGER = logging.getLogger(__name__)


class MockServer:

    def __init__(self):
        self.loop = asyncio.get_event_loop()

    def run(self):
        coro = asyncio.start_server(self.handler, HOST, PORT, loop=self.loop)
        self.loop.run_until_complete(coro)

    @staticmethod
    async def handler(reader, writer):
        try:
            while True:
                data = await reader.read(10000)
                if not data:
                    break
                LOGGER.debug(f"Server RECV: {data}")
                message = Payload.deserialize(data)

                if message.get('type') == 'publish' and message.get('replyAddress') == 'api.versions':
                    response = {"type": "message", "address": "api.versions", "headers": {},
                                "body": {"apiVersions": API_VERSION}}
                    binary_response = Payload.serialize(json.dumps(response))
                    logging.debug("Server SEND: %r" % binary_response)
                    writer.write(binary_response)
        finally:
            await writer.drain()
            LOGGER.debug("Close the client socket")
            writer.close()


@pytest.fixture
def setup_server():
    LOGGER.debug("Set up the server")
    server = MockServer()
    server.run()


@pytest.fixture
def setup_client():
    LOGGER.debug("Set up the client")
    client = EventBus(host=HOST, port=PORT)
    received_message_from_client = dict(data=None)

    def handle(text):
        received_message_from_client['body'] = text

    client.add_listen_func("api.versions", handle)
    return client, received_message_from_client


def test_client_functionality(setup_server, setup_client):
    client, received_message_from_client = setup_client
    client.connect()
    pub = Payload(type="publish", address="api.versions.get", replyAddress="api.versions")
    client.send(pub)
    time.sleep(1)
    assert received_message_from_client['body'] == {"apiVersions": API_VERSION}
    LOGGER.debug("Will tear down the server and the client")
    client.disconnect()
