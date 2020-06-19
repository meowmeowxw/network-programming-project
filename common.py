#!/usr/bin/env python3

import socket
from construct import Struct, Bytes, Int64un, Array, this, Byte


class Mac:
    def __init__(self, mac="FF:FF:FF:FF:FF:FF") -> None:
        self.mac = self.mac_to_bytes(mac)

    def mac_to_bytes(self, mac: str) -> bytes:
        return bytes.fromhex(mac.replace(":", ""))

    def __str__(self):
        return ":".join(f"{bytes([i]).hex()}" for i in self.mac)


class IP:
    def __init__(self, ip="10.10.10.10") -> None:
        self.ip = self.ip_to_bytes(ip)

    def ip_to_bytes(self, ip: str) -> bytes:
        return socket.inet_aton(ip)

    def __str__(self):
        return socket.inet_ntoa(self.ip)


header = Struct(
    "mac_src" / Bytes(6),
    "mac_dst" / Bytes(6),
    "ip_src" / Bytes(4),
    "ip_dst" / Bytes(4),
    # "msg_len" / Int64un,
    # "data" / Array(this.msg_len, Byte),
)

