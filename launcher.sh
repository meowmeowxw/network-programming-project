#!/bin/sh

python router.py &
sleep 0.5
python server.py &
sleep 0.5
python client-args.py 32:04:0A:EF:19:CF 92.10.10.15 &
sleep 0.5
python client-args.py 10:AF:CB:EF:19:CF 92.10.10.20 &
sleep 0.5
python client-args.py AF:04:67:EF:19:DA 92.10.10.25 &
