#!/usr/bin/env python3

import asyncore
import logging
import multiprocessing
import select
import socket
import sys
import time
import unicodedata

from common import *

arp_table = ARPTable()
# IP destination <----> Socket, MAC destination, MAC src
routing_table = {
    IP("195.1.10.10").ip: (
        ("localhost", 8200),
        Mac("55:04:0A:EF:10:AB"),
        Mac("32:03:0A:CF:10:DB"),
    ),
    IP("92.10.10").ip: (
        ("localhost", 8200),
        Mac("55:04:0A:EF:10:AB"),
        Mac("32:03:0A:CF:10:DB"),
    ),
}
clients = []


class Router:
    def __init__(self) -> None:
        self.mac_eth0 = Mac("32:03:0A:CF:10:DB")
        self.mac_eth1 = Mac("32:03:0A:DA:11:DC")
        self.RouterEth(8300, self.mac_eth0)
        self.RouterEth(8400, self.mac_eth1)

    class RouterEth(asyncore.dispatcher):
        def __init__(self, port: int, mac: Mac) -> None:
            asyncore.dispatcher.__init__(self)
            self.logger = logging.getLogger(f"Router {port}\t Mac: {mac}")
            self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
            self.set_reuse_addr()
            self.bind(("localhost", port))
            self.logger.debug(f"binding to {port}")
            self.listen(5)

        def handle_accept(self) -> None:
            client_info = self.accept()
            clients.append(client_info[0])
            print(f"client_info[0]: {client_info[0]}")
            if client_info is not None:
                self.logger.debug(f"handle_accept() -> {client_info[1]}")
                ClientHandler(client_info[0], client_info[1])


class ClientHandler(asyncore.dispatcher):
    def __init__(self, sock, address) -> None:
        asyncore.dispatcher.__init__(self, sock)
        self.logger = logging.getLogger(f"Client -> {address}")
        self.data_to_write = []
        self.first_time = True

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

        ip_dst = IP(hdr.get("ip_dst"))
        if self.first_time:
            sck = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.logger.debug(f"connecting to {ip_dst}")
            sck.connect(routing_table.get(ip_dst.ip)[0])
            self.server = ServerHandler(sck, self)
            self.first_time = False

        tmp = routing_table.get(ip_dst.ip, None)
        if tmp == None:
            mac_dst = routing_table.get(ip_dst.ip[:-1])[1].mac
            mac_src = routing_table.get(ip_dst.ip[:-1])[2].mac
        else:
            mac_dst = tmp[1].mac
            mac_src = tmp[2].mac
        hdr["mac_dst"] = mac_dst
        hdr["mac_src"] = mac_src
        self.logger.debug(f"ARP Table: {arp_table}")
        self.logger.debug(f"Packet new: {print_container(hdr)}")
        self.server.data_to_write.append(header.build(hdr) + payload)


class ServerHandler(asyncore.dispatcher):
    def __init__(self, sock, handler: ClientHandler) -> None:
        asyncore.dispatcher.__init__(self, sock)
        self.client = handler
        self.logger = logging.getLogger(f"Router -> Router/Server")
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
        self.logger.debug(f"adding data to write {data}\n")
        self.client.data_to_write.append(data)

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
