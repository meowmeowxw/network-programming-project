#!/usr/bin/env python3

import asyncore
import logging
import socket
from common import *


class Server(asyncore.dispatcher):
    online_clients = {}

    def __init__(self) -> None:
        asyncore.dispatcher.__init__(self)
        self.logger = logging.getLogger("Server: ")
        self.default_gateway = {("localhost", 8200): Mac("55:04:0A:EF:10:AB")}
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind(("localhost", 8000))
        self.logger.debug(f"binding to 8000")
        self.listen(5)

    def handle_accept(self) -> None:
        client_info = self.accept()
        if client_info is not None:
            self.logger.debug(f"handle_accept() -> {client_info[1]}")
            self.ClientHandler(client_info[0], client_info[1])

    class ClientHandler(asyncore.dispatcher):
        def __init__(self, sock, address) -> None:
            asyncore.dispatcher.__init__(self, sock)
            self.logger = logging.getLogger(f"Client -> {address}")
            self.data_to_write = []

        def writable(self):
            return bool(self.data_to_write)

        def handle_write(self) -> None:
            data = self.data_to_write.pop()
            sent = self.send(data[:1024])
            if sent < len(data):
                remaining = data[sent:]
                self.data_to_write.append(remaining)
            self.logger.debug('handle_write() -> (%d) "%s"', sent, data[:sent].rstrip())

        def handle_read(self) -> None:
            data = self.recv(1024)
            hdr = header.parse(data)
            print(hdr)
            payload = data[header.sizeof() :]
            self.logger.debug(
                f"handle_read() -> {len(data)}\t {print_container(hdr)}\t {payload}"
            )

        def handle_close(self) -> None:
            self.logger.debug("handle_close()")
            self.close()


def main():
    logging.basicConfig(
        level=logging.DEBUG, format="%(name)s\t[%(levelname)s]: %(message)s"
    )
    Server()
    asyncore.loop()


if __name__ == "__main__":
    main()
    pass


"""
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("localhost", 8000))
server.listen(2)
server_ip = "92.10.10.10"
server_mac = "00:00:0A:BB:28:FC"
router_mac = "05:10:0A:CB:24:EF"
while True:
    routerConnection, address = server.accept()
    if routerConnection != None:
        print(routerConnection)
        break
while True:
    ethernet_header = ""
    IP_header = ""

    message = input("\nEnter the text message to send: ")
    destination_ip = input(
        "Enter the IP of the clients to send the message to:\n1. 92.10.10.15\n2. 92.10.10.20\n3. 92.10.10.25\n"
    )
    if (
        destination_ip == "92.10.10.15"
        or destination_ip == "92.10.10.20"
        or destination_ip == "92.10.10.25"
    ):
        source_ip = server_ip
        IP_header = IP_header + source_ip + destination_ip

        source_mac = server_mac
        destination_mac = router_mac
        ethernet_header = ethernet_header + source_mac + destination_mac

        packet = ethernet_header + IP_header + message

        routerConnection.send(bytes(packet, "utf-8"))
    else:
        print("Wrong client IP inputted")
"""
