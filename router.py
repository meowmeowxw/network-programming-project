#!/usr/bin/env python3

import socket
import select
import sys
import time
import asyncio
import asyncore
import logging
from common import *


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
            self.address = self.socket.getsockname()
            self.logger.debug("binding to %s", self.address)
            self.listen(5)
            self.server_addr = ("localhost", 8000)

        def handle_accept(self) -> None:
            client_info = self.accept()
            if client_info is not None:
                self.logger.debug(f"handle_accept() -> {client_info[1]}")
                ClientHandler(client_info[0], client_info[1])


class ClientHandler(asyncore.dispatcher):
    def __init__(self, sock, address) -> None:
        asyncore.dispatcher.__init__(self, sock)
        self.logger = logging.getLogger(f"Client -> {address}")

    def handle_write(self) -> None:
        pass

    def handle_read(self) -> None:
        data = self.recv(1024)
        self.logger.debug(f"handle_read() -> {len(data)}\t {data}")

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

"""
clients = {
    "92.10.10.15": "32:04:0A:EF:19:CF",
    "92.10.10.20": "10:AF:CB:EF:19:CF",
    "92.10.10.25": "AF:04:67:EF:19:DA",
}

clients = dict((ip_to_bytes(k), mac_to_bytes(v)) for k, v in clients.items())
print(clients)
"""

"""
client1 = None
client2 = None
client3 = None

while client1 == None or client2 == None or client3 == None:
    client, address = router_eth0.accept()

    if client1 == None:
        client1 = client
        print("Client 1 is online")

    elif client2 == None:
        client2 = client
        print("Client 2 is online")
    else:
        client3 = client
        print("Client 3 is online")
arp_table_socket = {client1_ip: client1, client2_ip: client2, client3_ip: client3}
arp_table_mac = {
    client1_ip: client1_mac,
    client2_ip: client2_mac,
    client3_ip: client3_mac,
}
"""

"""
router_eth1.connect(server)
while True:
    received_message = router_eth1.recv(1024)
    received_message = received_message.decode("utf-8")

    source_mac = received_message[0:17]
    destination_mac = received_message[17:34]
    source_ip = received_message[34:45]
    destination_ip = received_message[45:56]
    message = received_message[56:]

    print(
        "The packed received:\n Source MAC address: {source_mac}, Destination MAC address: {destination_mac}".format(
            source_mac=source_mac, destination_mac=destination_mac
        )
    )
    print(
        "\nSource IP address: {source_ip}, Destination IP address: {destination_ip}".format(
            source_ip=source_ip, destination_ip=destination_ip
        )
    )
    print("\nMessage: " + message)

    ethernet_header = router_mac + arp_table_mac[destination_ip]
    IP_header = source_ip + destination_ip
    packet = ethernet_header + IP_header + message

    destination_socket = arp_table_socket[destination_ip]

    destination_socket.send(bytes(packet, "utf-8"))
    time.sleep(2)
"""
