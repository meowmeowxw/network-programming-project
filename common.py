#!/usr/bin/env python3

import socket
from construct import Struct, Bytes


def print_mac(mac: bytes) -> None:
    print(":".join(f"{bytes([i]).hex()}" for i in mac))


def print_ip(ip: bytes) -> None:
    print(socket.inet_ntoa(ip))


def ip_to_bytes(ip: str) -> bytes:
    return socket.inet_aton(ip)


def mac_to_bytes(mac: str) -> bytes:
    return bytes.fromhex(mac.replace(":", ""))


header = Struct(
    "mac_src" / Bytes(6),
    "mac_dst" / Bytes(6),
    "ip_src" / Bytes(4),
    "ip_dst" / Bytes(4),
)

