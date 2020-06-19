import common

h = common.header.build(
    dict(mac_src=b"a" * 6, mac_dst=b"b" * 6, ip_src=b"c" * 4, ip_dst=b"d" * 4)
)
print(h)
