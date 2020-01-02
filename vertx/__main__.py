import logging
import sys
import time
import json
from vertx.eventbus import EventBus, Payload

LOGGER = logging.getLogger(__name__)


class Client:

    def __init__(self, host, port):
        self.eb = EventBus(host, port)

    def parse(self, text):
        current = Payload()
        try:
            current.data = json.loads(text)
        except json.decoder.JSONDecodeError:
            LOGGER.error("Not valid JSON format")
        else:
            self.eb.send(current)

    def quit(self):
        sys.stderr, sys.stdout = None, None
        self.eb.disconnect()
        time.sleep(2)
        sys.exit(0)


def main():
    try:
        args = sys.argv[1].split(':')
        host, port = args[0], int(args[1])
    except (IndexError, ValueError):
        raise ValueError("Please input a parameter such as localhost:1999")
    cli = Client(host=host, port=port)
    cli.eb.connect()

    try:
        while True:
            command = input("> ")
            command = command.strip()
            if not command:
                continue
            if command == "exit":
                cli.quit()
            else:
                cli.parse(command)
    except (KeyboardInterrupt, EOFError):  # ^C, ^D
        cli.quit()


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s - %(pathname)s - %(levelname)s: %(message)s', datefmt='%x %I:%M:%S',
                        level=logging.INFO)
    main()
