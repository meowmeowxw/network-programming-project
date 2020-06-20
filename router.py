#!/usr/bin/env python3

import asyncore
import logging
import select
import socket
import sys
import time
import unicodedata
import multiprocessing

from common import *


# arp_table = multiprocessing.Manager().dict()
arp_table = ARPTable()


class Router:
    def __init__(self) -> None:
        self.mac_eth0 = Mac("55:04:0A:EF:11:CF")
        self.mac_eth1 = Mac("55:04:0A:EF:10:AB")
        self.RouterEth(8100, self.mac_eth0)
        self.RouterEth(8200, self.mac_eth1)

    class RouterEth(asyncore.dispatcher):
        def __init__(self, port: int, mac: Mac) -> None:
            asyncore.dispatcher.__init__(self)
            self.logger = logging.getLogger(f"Router {port}\t Mac: {mac}")
            self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
            self.set_reuse_addr()
            self.bind(("localhost", port))
            self.logger.debug(f"binding to {port}")
            self.listen(5)
            self.server_addr = ("localhost", 8000)

        def handle_accept(self) -> None:
            client_info = self.accept()
            print(f"client_info[0]: {client_info[0]}")
            if client_info is not None:
                self.logger.debug(f"handle_accept() -> {client_info[1]}")
                ClientHandler(client_info[0], client_info[1])


class ClientHandler(asyncore.dispatcher):
    def __init__(self, sock, address) -> None:
        asyncore.dispatcher.__init__(self, sock)
        self.logger = logging.getLogger(f"Client -> {address}")
        self.data_to_write = [b"> welcome back"]
        self.server_addr = ("localhost", 8000)

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
        mac_src = hdr.get("mac_src")
        ip_src = hdr.get("ip_src")
        if mac_src not in arp_table.keys():
            arp_table[mac_src] = ip_src
        else:
            if ip_src != arp_table.get(mac_src):
                self.logger.debug(f"MAC Spoofing detected -> {IP(ip_src)}")

        mac_dst = hdr.get("mac_dst")
        hdr["mac_dst"] = Mac("52:AB:0A:DF:10:DC").mac
        ip_dst = hdr.get("ip_dst")
        self.logger.debug(f"ARP Table: {arp_table}")
        self.logger.debug(f"Packet new: {print_container(hdr)}")
        srv_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        srv_socket.connect(self.server_addr)
        ServerHandler(srv_socket, header.build(hdr) + payload)
        # self.connect(self.server_addr)
        # self.send(header.build(hdr) + payload)


class ServerHandler(asyncore.dispatcher):
    def __init__(self, sock, data) -> None:
        asyncore.dispatcher.__init__(self, sock)
        self.logger = logging.getLogger(f"Router -> Server")
        self.data_to_write = [b"> welcome back"]
        self.server_addr = ("localhost", 8000)
        self.data_to_write = [data]

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

    def handle_close(self) -> None:
        self.logger.debug("handle_close()")
        self.close()


def main():
    logging.basicConfig(
        level=logging.DEBUG, format="%(name)s\t[%(levelname)s]: %(message)s"
    )
    Router()
    asyncore.loop()


if __name__ == "__main__":
    main()

