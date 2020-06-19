#!/usr/bin/env python3

from construct import *

header = Struct(
    "mac_src" / Bytes(6), "mac_dst" / Bytes(6), "ip_src" / Bytes(4), "ip_dst" / Bytes(4)
)
