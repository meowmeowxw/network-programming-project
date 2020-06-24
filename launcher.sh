#!/bin/sh

python3 router1.py &
sleep 0.5
python3 router2.py &
sleep 0.5
python3 server.py &
sleep 0.5
python3 client-args.py 32:04:0A:EF:19:CF 92.10.10.15 55:04:0A:EF:11:CF 8100 &
sleep 0.5
python3 client-args.py 10:AF:CB:EF:19:CF 92.10.10.20 55:04:0A:EF:11:CF 8100 &
sleep 0.5
python3 client-args.py AF:04:67:EF:19:DA 92.10.10.25 55:04:0A:EF:11:CF 8100 &
sleep 0.5
python3 client-args.py 42:A3:1B:DA:12:AC 1.5.10.15 32:03:0A:DA:11:DC 8400 &
sleep 0.5
python3 client-args.py 42:A3:5B:DA:13:EF 1.5.10.20 32:03:0A:DA:11:DC 8400 &
sleep 0.5
python3 client-args.py 44:BF:5B:DA:11:AC 1.5.10.30 32:03:0A:DA:11:DC 8400 &
