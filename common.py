#!/usr/bin/env python3

import functools
import socket

from construct import Array, Byte, Bytes, Container, Enum, Int64un, Struct, this


def multidispatch_mac(*types):
    def register(function):
        name = function.__name__
        mm = multidispatch_mac.registry.get(name)
        if mm is None:

            @functools.wraps(function)
            def wrapper(self, *args):
                types = tuple(arg.__class__ for arg in args)
                function = wrapper.typemap.get(types)
                if function is None:
                    raise TypeError("no match")
                return function(self, *args)

            wrapper.typemap = {}
            mm = multidispatch_mac.registry[name] = wrapper
        if types in mm.typemap:
            raise TypeError("duplicate registration")
        mm.typemap[types] = function
        return mm

    return register


def multidispatch_ip(*types):
    def register(function):
        name = function.__name__
        mm = multidispatch_ip.registry.get(name)
        if mm is None:

            @functools.wraps(function)
            def wrapper(self, *args):
                types = tuple(arg.__class__ for arg in args)
                function = wrapper.typemap.get(types)
                if function is None:
                    raise TypeError("no match")
                return function(self, *args)

            wrapper.typemap = {}
            mm = multidispatch_ip.registry[name] = wrapper
        if types in mm.typemap:
            raise TypeError("duplicate registration")
        mm.typemap[types] = function
        return mm

    return register


multidispatch_mac.registry = {}
multidispatch_ip.registry = {}


class Mac:
    @multidispatch_mac(str)
    def __init__(self, mac) -> None:
        self.mac = self.__mac_to_bytes(mac)

    @multidispatch_mac(bytes)
    def __init__(self, mac) -> None:
        self.mac = mac

    def __str__(self):
        return ":".join(f"{bytes([i]).hex()}" for i in self.mac).upper()

    def __mac_to_bytes(self, mac: str) -> bytes:
        return bytes.fromhex(mac.replace(":", ""))


class IP:
    @multidispatch_ip(str)
    def __init__(self, ip) -> None:
        self.ip = self.__ip_to_bytes(ip)

    @multidispatch_ip(bytes)
    def __init__(self, ip) -> None:
        self.ip = ip

    def __str__(self):
        return socket.inet_ntoa(self.ip)

    def __ip_to_bytes(self, ip: str) -> bytes:
        return socket.inet_aton(ip)


class ARPTable(dict):
    def __setitem__(self, key, item):
        self.__dict__[key] = item

    def __getitem__(self, key):
        return self.__dict__[key]

    def __str__(self) -> str:
        return "".join(f"{Mac(k)} | {IP(v)}\t" for k, v in self.__dict__.items())


def print_container(hdr: Container) -> str:
    first_time = True
    s = ""
    for k, v in hdr.items():
        if first_time:
            first_time = False
            continue
        if len(v) == 6:
            s += f"{k}: {Mac(v)} | "
        else:
            s += f"{k}: {IP(v)} | "
    return s


header = Struct(
    "mac_src" / Bytes(6),
    "mac_dst" / Bytes(6),
    "ip_src" / Bytes(4),
    "ip_dst" / Bytes(4),
)


class Header(Container):
    def __setitem__(self, key, item):
        self.__dict__[key] = item

    def __getitem__(self, key):
        return self.__dict__[key]

    def __str__(self):
        first_time = True
        s = ""
        for k, v in self.__dict__.items():
            if first_time:
                first_time = False
                continue
            if len(v) == 6:
                s += f"{k}: {Mac(v)} | "
            else:
                s += f"{k}: {IP(v)} | "
        return s
