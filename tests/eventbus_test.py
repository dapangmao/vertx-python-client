import logging
import json
import time
import asyncio

from vertx import EventBus, Payload

API_VERSION = 1.1
PORT = 8765
HOST = '127.0.0.1'


def assert_messsage_from_client(body):
    logging.debug("Will assert the API version")
    assert body == {"apiVersions": API_VERSION}, "The message from the server is not expected"


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
                logging.debug(f"Server RECV: {data}")
                message = Payload.deserialize(data)

                if message.get('type') == 'publish' and message.get('replyAddress') == 'api.versions':
                    response = {"type": "message", "address": "api.versions", "headers": {},
                                "body": {"apiVersions": API_VERSION}}
                    binary_response = Payload.serialize(json.dumps(response))
                    logging.debug("Server SEND: %r" % binary_response)
                    writer.write(binary_response)
        finally:
            await writer.drain()
            logging.debug("Close the client socket")
            writer.close()


def test_client_functionality():
    logging.debug("Will set up both the server and the client")
    server = MockServer()
    server.run()

    client = EventBus(host=HOST, port=PORT)
    client.add_listen_func("api.versions", lambda x: assert_messsage_from_client(x))
    client.connect()

    pub = Payload(type="publish", address="api.versions.get", replyAddress="api.versions")
    client.send(pub)
    time.sleep(1)
    logging.debug("Will tear down the server and the client")
    client.disconnect()
