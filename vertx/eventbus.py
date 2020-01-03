import asyncio
import threading
import json
import struct
import logging
import sys

from typing import Optional, Callable

LOGGER = logging.getLogger(__name__)


class Payload:

    def __init__(self, type="ping", address=None, replyAddress=None, header=None, body=None):
        # type: (str, Optional[str], Optional[str], Optional[dict], Optional[dict]) -> None
        self.data = {"type": type}
        if address:
            self.data["address"] = address
        if replyAddress:
            self.data["replyAddress"] = replyAddress
        if header:
            self.data["header"] = header
        if body:
            self.data["body"] = body

    def __repr__(self):
        return json.dumps(self.data)

    def to_binary(self):
        return self.serialize(self.__repr__())

    @staticmethod
    def serialize(text):
        # type: (str) -> bytes
        msg = text.encode()
        return struct.pack("!i%ss" % len(msg), len(msg), msg)

    @staticmethod
    def deserialize(byte_array):
        # type: (bytes) -> dict
        length = int.from_bytes(byte_array[:4], 'big')
        try:
            _text = byte_array[4: 4+length]
        except IndexError:
            LOGGER.error(f"The incoming data has incorrect length")
            return {}
        else:
            text = _text.decode()
        return json.loads(text)


class EventBus:

    def __init__(self, host, port, ping_interval_by_seconds=20):
        # type: (str, int, int) -> None
        self.host = host
        self.port = port
        self.ping_interval_by_seconds = ping_interval_by_seconds
        self.loop = asyncio.get_event_loop()
        self.daemon = threading.Thread(target=self.loop.run_forever, name="event-bus-async")
        self.stop_sign = self.loop.create_future()  # type: asyncio.Future[None]  # add a stop sign to control the loop
        self.inputs = asyncio.Queue(loop=self.loop)
        self.listen_funcs = {}  # type: dict[str, Callable]

    async def _connect_then_listen(self):
        reader, writer = await asyncio.open_connection(self.host, self.port)
        try:
            while True:
                incoming = asyncio.ensure_future(reader.read(sys.maxsize))  # look for EOL since the default parameter -1 does not work # noqa
                outgoing = asyncio.ensure_future(self.inputs.get())
                done, pending = await asyncio.wait([incoming, outgoing, self.stop_sign],
                                                   return_when=asyncio.FIRST_COMPLETED)  # type: set[asyncio.Future], set[asyncio.Future]  # noqa
                # Cancel pending tasks to avoid leaking them
                if incoming in pending:
                    incoming.cancel()
                if outgoing in pending:
                    outgoing.cancel()

                if outgoing in done:
                    msg = outgoing.result()
                    writer.write(msg.to_binary())
                    LOGGER.debug(f"Client SEND: {msg}")
                    await writer.drain()
                if incoming in done:
                    msg = incoming.result()
                    LOGGER.debug(f"Client RECV: {msg}")
                    obj = Payload.deserialize(msg)
                    self.listen(obj)
                if self.stop_sign in done:
                    break
        finally:
            await writer.close()
            self.disconnect()

    async def ping(self):
        """ Use a ping operation to keep long polling """
        while True:
            self.send(Payload())
            await asyncio.sleep(self.ping_interval_by_seconds)

    def send(self, payload):
        # type: (Payload) -> None
        address = payload.data.get("address")
        if address and payload.data.get('type') == "register" and address not in self.listen_funcs:
            self.listen_funcs[address] = lambda x: LOGGER.info(f'ADDRESS {address} RECV: {x}')
        elif address and payload.data.get('type') == "unregister" and address in self.listen_funcs:
            del self.listen_funcs[address]
        self.loop.call_soon_threadsafe(self.inputs.put_nowait, payload)

    def connect(self):
        self.loop.create_task(self._connect_then_listen())
        self.loop.create_task(self.ping())
        self.daemon.start()

    def disconnect(self):
        self.loop.call_soon_threadsafe(self.stop_sign.set_result, None)  # break the event loop
        self.loop.stop()  # stop the event loop
        self.daemon.join()  # stop the thread

    def listen(self, dictionary):
        # type: (dict) -> None
        if 'address' not in dictionary or 'body' not in dictionary:
            return
        address, body = dictionary["address"], dictionary["body"]
        func = self.listen_funcs.get(address)
        if func:
            func(body)

    def add_listen_func(self, address, action):
        # type: (str, Callable) -> None
        self.listen_funcs[address] = action

    def delete_listen_func(self, address):
        # type: (str) -> None
        try:
            del self.listen_funcs[address]
        except KeyError:
            LOGGER.error(f"There is no listening function for {address}")
