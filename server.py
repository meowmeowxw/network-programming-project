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
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind(("localhost", 8000))
        self.logger.debug(f"binding to 8000")
        self.listen(5)

    def handle_accept(self) -> None:
        client_info = self.accept()
        # Pass connection to the ClientHandler
        if client_info is not None:
            self.logger.debug(f"handle_accept() -> {client_info[1]}")
            cl = self.ClientHandler(client_info[0], client_info[1])
            # Add the clients to the list of clients
            clients.append(cl)

    class ClientHandler(asyncore.dispatcher):
        def __init__(self, sock, address) -> None:
            asyncore.dispatcher.__init__(self, sock)
            self.first_time = True
            self.logger = logging.getLogger(f"Client -> {address}")
            self.ip_client = None
            self.online = True
            # self.data_to_write = [b"Server: welcome back"]
            self.data_to_write = []

        def writable(self):
            return bool(self.data_to_write)

        def add_data(self, data: bytes) -> None:
            self.data_to_write.append(self.__build_header(self.ip_client) + data)

        # Send data back to the router
        def handle_write(self) -> None:
            data = self.data_to_write.pop()
            sent = self.send(data[:1024])
            if sent < len(data):
                remaining = data[sent:]
                self.data_to_write.append(remaining)
            self.logger.debug('handle_write() -> (%d) "%s"', sent, data[:sent].rstrip())

        # Read and parse message
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
            # Say welcome to the new client, and informs the other clients
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
                self.online = True
            elif data.startswith(b"offline"):
                if self.ip_client in online_clients:
                    online_clients.remove(self.ip_client)
                self.online = False
            # Send list of active clients
            elif data.startswith(b"get_clients"):
                f = ",".join(str(i) for i in online_clients)
                self.add_data(f.encode())
            # Send private message to an ip specified in the destination
            elif data.startswith(b"message:"):
                if self.online:
                    splitted = data.split(b",")
                    ip_dst = IP(splitted[0].decode().replace("message:", ""))
                    data_to_send = splitted[1]
                    self.logger.debug(f"sending {data_to_send} to {ip_dst}")
                    for i in clients:
                        if i.ip_client.ip == ip_dst.ip:
                            if i.online:
                                self.logger.debug(f"{i.ip_client}")
                                i.add_data(
                                    b"> "
                                    + str(self.ip_client).encode()
                                    + b": "
                                    + data_to_send
                                )
                            else:
                                self.add_data(f"> {ip_dst} is offline".encode())
                                break
                else:
                    self.add_data(b"> You are offline")
            # Send public message to everyone
            elif data.startswith(b"broadcast:"):
                if self.online:
                    data_to_send = data.split(b":")[1]
                    for i in clients:
                        if i != self and i.online:
                            i.add_data(
                                b"> "
                                + str(self.ip_client).encode()
                                + b": "
                                + data_to_send
                            )
                else:
                    self.add_data(b"> You are offline")

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
