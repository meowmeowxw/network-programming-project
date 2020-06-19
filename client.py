#!/usr/bin/env python3

import asyncore
import socket

from common import *


class Client(asyncore.dispatcher):
    def __init__(self) -> None:
        asyncore.dispatcher.__init__(self)
        self.server = ("localhost", 8000)
        self.default_gateway = {("localhost", 8100): Mac("55:04:0A:EF:11:CF")}
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect(self.default_gateway[0])

    def handle_connect(self):
        pass

    def handle_close(self):
        self.close()

    def handle_read(self):
        self.recv(4096)

    def writable(self):
        return True

    def handle_write(self, msg):
        self.send(msg)


def main():
    pass


if __name__ == "__main__":
    main()
