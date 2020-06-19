#!/usr/bin/env python3

import socket
from construct import Struct, Bytes, Int64un, Array, this, Byte, Container


class Mac:
    def __init__(self, mac="FF:FF:FF:FF:FF:FF") -> None:
        self.mac = self.__mac_to_bytes(mac)

    def __str__(self):
        return ":".join(f"{bytes([i]).hex()}" for i in self.mac)

    def __mac_to_bytes(self, mac: str) -> bytes:
        return bytes.fromhex(mac.replace(":", ""))


class IP:
    def __init__(self, ip="10.10.10.10") -> None:
        self.ip = self.__ip_to_bytes(ip)

    def __str__(self):
        return socket.inet_ntoa(self.ip)

    def __ip_to_bytes(self, ip: str) -> bytes:
        return socket.inet_aton(ip)


def mac_to_str(mac: bytes) -> str:
    return ":".join(f"{bytes([i]).hex()}" for i in mac)


def ip_to_str(ip: bytes) -> str:
    return socket.inet_ntoa(ip)


def print_container(hdr: Container) -> str:
    first_time = True
    s = ""
    for k, v in hdr.items():
        if first_time:
            first_time = False
            continue
        if len(v) == 6:
            s += f"{k}: {mac_to_str(v)} | "
        else:
            s += f"{k}: {ip_to_str(v)} | "
    return s


header = Struct(
    "mac_src" / Bytes(6),
    "mac_dst" / Bytes(6),
    "ip_src" / Bytes(4),
    "ip_dst" / Bytes(4),
)

