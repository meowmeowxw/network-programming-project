import common

h = common.header.build(
    dict(
        mac_src=b"a" * 6,
        mac_dst=b"b" * 6,
        ip_src=b"c" * 4,
        ip_dst=b"d" * 4,
        # msg_len=20,
        # data=b"data".zfill(20),
    )
)
hdr = common.header.parse(h)

m = common.Mac(b"aaaaaa")
print(m)
m1 = common.Mac("DF:FF:AB:2E:3F:A4")
print(m1)
i = common.IP(b"bbbb")
i1 = common.IP("192.168.1.1")
print(i)
print(i1)
hh = common.Header(common.header.parse(h))
print(hh)
