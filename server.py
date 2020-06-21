#!/usr/bin/env python3

import asyncore
import logging
import socket

from common import *

online_clients = set()
clients = []
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
            cl = self.ClientHandler(client_info[0], client_info[1])
            clients.append(cl)

    class ClientHandler(asyncore.dispatcher):
        def __init__(self, sock, address) -> None:
            asyncore.dispatcher.__init__(self, sock)
            self.first_time = True
            self.logger = logging.getLogger(f"Client -> {address}")
            self.ip_client = None
            # self.data_to_write = [b"Server: welcome back"]
            self.data_to_write = []

        def writable(self):
            return bool(self.data_to_write)

        def add_data(self, data: bytes) -> None:
            self.data_to_write.append(self.__build_header(self.ip_client) + data)

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
            self.__parse_message(hdr, payload)

        def handle_close(self) -> None:
            self.logger.debug("handle_close()")
            self.close()

        def __parse_message(self, header: Container, data: bytes) -> None:
            if self.first_time:
                self.ip_client = IP(header.get("ip_src"))
                self.add_data(f"> welcome {self.ip_client}".encode())
                for i in clients:
                    i.add_data(
                        f"new client: {self.ip_client}".encode()
                    ) if i != self else None
                self.first_time = False

            if data.startswith(b"online"):
                online_clients.add(self.ip_client)
            elif data.startswith(b"offline"):
                online_clients.remove(self.ip_client)
            elif data.startswith(b"get_clients"):
                f = ",".join(str(i) for i in online_clients)
                self.add_data(f.encode())
            elif data.startswith(b"message:"):
                splitted = data.split(b",")
                #self.logger.debug(f"sending {splitted}")
                #self.logger.debug(f"{splitted[0].decode().replace("message")})
                ip_dst = IP(splitted[0].decode().replace("message:", ""))
                data_to_send = splitted[1]
                self.logger.debug(f"sending {data_to_send} to {ip_dst}")
                for i in clients:
                    self.logger.debug(f"{i.ip_client}")
                    if i.ip_client.ip == ip_dst.ip:
                        i.add_data(b"> " + str(ip_dst).encode() + b": " + data_to_send)

        def __build_header(self, ip_dst: IP) -> bytes:
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
