#!/usr/bin/env python3

import asyncore
import logging
import socket
from common import *


online_clients = set()

mac_server = Mac("52:AB:0A:DF:10:DC")
mac_gateway = Mac("55:04:0A:EF:10:AB")
ip_server = IP("195.1.10.10")


class Server(asyncore.dispatcher):
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
            # self.data_to_write = [b"Server: welcome back"]
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
            payload = data[header.sizeof() :]
            self.logger.debug(
                f"handle_read() -> {len(data)}\t {print_container(hdr)}\t {payload}"
            )
            ip_client = IP(hdr.get("ip_src"))
            online_clients.add(ip_client) if payload == b"online" else None
            online_clients.remove(ip_client) if payload == b"offline" else None
            self.data_to_write.append(self.__build_header(ip_client) + b"> welcome")

        def handle_close(self) -> None:
            self.logger.debug("handle_close()")
            self.close()

        def __build_header(self, ip_dst) -> bytes:
            return header.build(
                dict(
                    mac_src=mac_server.mac,
                    mac_dst=mac_gateway.mac,
                    ip_src=ip_server.ip,
                    ip_dst=ip_dst.ip,
                )
            )


def main():
    logging.basicConfig(
        level=logging.DEBUG, format="%(name)s\t[%(levelname)s]: %(message)s"
    )
    Server()
    asyncore.loop()


if __name__ == "__main__":
    main()
