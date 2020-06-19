#!/usr/bin/env python3

import socket
from construct import Struct, Bytes, Int64un, Array, this, Byte


def print_mac(mac: bytes) -> None:
    print(":".join(f"{bytes([i]).hex()}" for i in mac))


def print_ip(ip: bytes) -> None:
    print(socket.inet_ntoa(ip))


def ip_to_bytes(ip: str) -> bytes:
    return socket.inet_aton(ip)


def mac_to_bytes(mac: str) -> bytes:
    return bytes.fromhex(mac.replace(":", ""))


class Layer2:
    def __init__(self, mac_src: bytes, mac_dst: bytes) -> None:
        self.mac_src = mac_src
        self.mac_dst = mac_dst


class Layer3:
    def __init__(self, ip_src: bytes, ip_dst: bytes) -> None:
        self.ip_src = ip_src
        self.ip_dst = ip_dst


header = Struct(
    "mac_src" / Bytes(6),
    "mac_dst" / Bytes(6),
    "ip_src" / Bytes(4),
    "ip_dst" / Bytes(4),
    # "msg_len" / Int64un,
    # "data" / Array(this.msg_len, Byte),
)

