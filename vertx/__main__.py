import sys
import logging
import cmd
import threading
from typing import List

from .eventbus import EventBusAsync

LOGGER = logging.getLogger(__name__)


class Client:

    def __init__(self, host: str, port: int):
        self.eb = EventBusAsync(host, port)
        self.eb.cli_mode = True
        self.daemon = threading.Thread(target=self.eb.loop.run_forever)

    def connect(self):
        self.eb.connect()
        self.daemon.start()

    def quit(self):
        self.daemon.join()
        self.eb.disconnect()


class Shell(cmd.Cmd):
    intro = "Welcome to the VertX shell. Type help or ? to list commands.\nPress CTRL+C twice to quit\n"
    prompt = ">> "
    client = None

    def preloop(self):
        args: List[str] = sys.argv
        if len(args) == 2:
            arglist = args[1].split(":")
        elif len(args) == 3:
            arglist = args[1:]
        else:
            raise IOError(f"Not correct argument number: {arglist}")
        host, port = arglist[0], int(arglist[1])
        self.client = Client(host=host, port=port)
        self.client.connect()

    def default(self, line: str):
        """
        Example
            {"type": "register", "address": "app.version"}
            {"type": "publish", "address": "app.version.get", "replyAddress": "app.version"}
        """
        self.client.eb.send_text(line)

    def do_debug(self, arg: str):
        """Enable the debug mode"""
        logging.getLogger().setLevel(logging.DEBUG)
        logging.info("Will enable the debug mode")

    def do_quit(self, arg: str):
        """Type quit to quit the program"""
        self.client.quit()

    def emptyline(self):
        pass


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s - %(levelname)s: %(message)s', datefmt='%x %I:%M:%S', level=logging.INFO)
    Shell().cmdloop()
