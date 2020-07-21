import asyncio
import json
import struct
import logging
import sys
from typing import Optional, Callable, Set, Dict

LOGGER = logging.getLogger(__name__)


class EventBusPayload:
    def __init__(
        self,
        type: str = "ping",
        address: Optional[str] = None,
        replyAddress: Optional[str] = None,
        header: Optional[Dict] = None,
        body: Optional[Dict] = None,
    ):
        self.data = dict(
            type=type,
            address=address,
            replyAddress=replyAddress,
            header=header,
            body=body,
        )

    def __repr__(self):
        return json.dumps(self.data)

    def to_binary(self):
        return self.serialize(self.__repr__())

    @staticmethod
    def serialize(text: str) -> bytes:
        msg = text.encode()
        return struct.pack("!i%ss" % len(msg), len(msg), msg)

    @staticmethod
    def deserialize(byte_array: bytes) -> Dict[str, str]:
        try:
            length = int.from_bytes(byte_array[:4], "big")
            _text = byte_array[4: 4 + length]
            text = _text.decode()
            return json.loads(text)
        except (IndexError, json.decoder.JSONDecodeError):
            LOGGER.error(f"Cannot decode the original bytes: {byte_array}")
            return {}


class EventBusAsync:
    def __init__(self, hostname: str, port: int):
        self.host = hostname
        self.port = port
        self.loop = asyncio.get_event_loop()
        self.stop_sign: asyncio.Future[
            None
        ] = self.loop.create_future()  # add a stop sign to control the loop
        self.inputs = asyncio.Queue(loop=self.loop)
        self.on_funcs: Dict[str, Callable] = {}
        self.cli_mode = False

    async def _listen(self):
        reader, writer = await asyncio.open_connection(self.host, self.port)
        try:
            while True:
                incoming = asyncio.ensure_future(
                    reader.read(sys.maxsize - 1)
                )  # asyncio has a bug that does not honor the default parameter -1 # noqa
                outgoing = asyncio.ensure_future(self.inputs.get())
                done, pending = await asyncio.wait(
                    [incoming, outgoing, self.stop_sign],
                    return_when=asyncio.FIRST_COMPLETED,
                )  # type: Set[asyncio.Future], Set[asyncio.Future]
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
                    if msg == b"":
                        LOGGER.warning("Received disconnection signal from the server")
                        break
                    LOGGER.debug(f"Client RECV: {msg}")
                    obj = EventBusPayload.deserialize(msg)
                    self._handle_incoming_message(obj)
                if self.stop_sign in done:
                    break
        finally:
            await writer.close()
            self.disconnect()

    async def _ping(self, ping_interval_by_seconds=20):
        """ Use a ping operation to keep long polling """
        while True:
            self.publish(EventBusPayload())
            await asyncio.sleep(ping_interval_by_seconds)

    def publish(self, payload: EventBusPayload):
        address: Optional[str] = payload.data.get("address")
        if (
            address
            and payload.data.get("type") == "register"
            and address not in self.on_funcs
        ):
            self.on_funcs[address] = lambda x: LOGGER.info(
                f"ADDR: {address} - RECV: {x}"
            )
        elif (
            address
            and payload.data.get("type") == "unregister"
            and address in self.on_funcs
        ):
            del self.on_funcs[address]
        self.loop.call_soon_threadsafe(self.inputs.put_nowait, payload)

    def connect(self):
        self.loop.create_task(self._listen())
        self.loop.create_task(self._ping())

    def disconnect(self):
        self.loop.call_soon_threadsafe(
            self.stop_sign.set_result, None
        )  # break the event loop

    def _handle_incoming_message(self, dictionary: Dict[str, str]):
        if self.cli_mode:
            LOGGER.info(dictionary)
            return
        if "address" not in dictionary or "body" not in dictionary:
            return
        address, body = dictionary["address"], dictionary["body"]
        func = self.on_funcs.get(address)
        if func:
            func(body)

    def subscribe(self, address: str, action: Callable):
        self.on_funcs[address] = action

    def unsubscribe(self, address: str):
        if address in self.on_funcs:
            del self.on_funcs[address]
        else:
            LOGGER.error(f"There is no listening function for {address}")

    def send_text(self, text: str):
        current = EventBusPayload()
        try:
            current.data = json.loads(text)
        except json.decoder.JSONDecodeError:
            LOGGER.error(f"Not a valid JSON format: {text}")
        else:
            self.publish(current)
