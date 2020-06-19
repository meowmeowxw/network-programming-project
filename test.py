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
common.pprint(hdr)
