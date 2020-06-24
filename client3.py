#!/usr/bin/env python3

import asyncore
import logging
import socket
import sys
import threading
import tkinter

from common import *


class Client:
    def __init__(
        self, mac_client: str, ip_client: str, mac_gateway: str, gateway_port: str
    ) -> None:
        self.mac_client = Mac(mac_client)
        self.ip_client = IP(ip_client)
        self.ip_server = IP("195.1.10.10")
        self.mac_gateway = Mac(mac_gateway)
        self.default_gateway = ("localhost", int(gateway_port))

        self.logger = logging.getLogger(f"Client {self.ip_client} ")

        self.window = tkinter.Tk()
        self.window.title(f"{self.ip_client}")
        self.messages_frame = tkinter.Frame(self.window)
        self.message = tkinter.StringVar()
        self.to_ip = tkinter.StringVar()
        self.to_ip.set("Write here client ip, message option must be selected")
        self.message.set("Write here your message")
        self.scrollbar = tkinter.Scrollbar(self.messages_frame)
        self.msg_list = tkinter.Listbox(
            self.messages_frame, height=15, width=80, yscrollcommand=self.scrollbar.set
        )
        self.scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
        self.msg_list.pack(side=tkinter.LEFT, fill=tkinter.BOTH)
        self.msg_list.pack()
        self.messages_frame.pack()
        self.entry_field = tkinter.Entry(
            self.window, width=80, textvariable=self.message
        )
        self.entry_ip = tkinter.Entry(self.window, width=80, textvariable=self.to_ip)
        self.entry_ip.pack()
        # leghiamo la funzione send al tasto Return
        self.entry_field.bind("<Return>", self.send_message)

        self.entry_field.pack()
        # creiamo il tasto invio e lo associamo alla funzione send
        send_button = tkinter.Button(
            self.window, text="Send", command=self.send_message
        )
        # integriamo il tasto nel pacchetto
        send_button.pack()

        self.options = tkinter.Listbox(self.window)
        self.options.insert(1, "online")
        self.options.insert(2, "offline")
        self.options.insert(3, "get_clients")
        self.options.insert(4, "message")
        self.options.insert(5, "broadcast")
        self.options.pack()

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect(self.default_gateway)
        self.data_to_write = [b"online"]
        self.handle_write()

    def handle_close(self):
        self.logger.debug(f"handle_close()")
        self.socket.close()

    def handle_read(self):
        while True:
            try:
                data = self.socket.recv(512)
                self.logger.debug(f"handle_read() -> {data}")
                self.msg_list.insert(tkinter.END, data[header.sizeof() :])
            except:
                self.handle_close()
                exit(0)

    def handle_write(self) -> None:
        while self.data_to_write:
            data = self.data_to_write.pop()
            self.msg_list.insert(tkinter.END, data)
            hdr = self.__build_header()
            sent = self.socket.send(hdr + data)
            self.logger.debug(f"handle_write() -> {sent}: {data[:sent].rstrip()}")
            if sent < len(data):
                remaining = data[sent:]
                self.data_to_write.append(remaining)

    def send_message(self):
        sel = self.options.get(self.options.curselection()[0])
        print(f"{self.to_ip.get()}")
        if sel == "message":
            sel += ":" + self.to_ip.get() + "," + self.message.get()
        elif sel == "broadcast":
            sel += ":" + self.message.get()
        self.data_to_write.append(sel.encode())
        self.handle_write()

    def __build_header(self) -> bytes:
        return header.build(
            dict(
                mac_src=self.mac_client.mac,
                mac_dst=self.mac_gateway.mac,
                ip_src=self.ip_client.ip,
                ip_dst=self.ip_server.ip,
            )
        )


def main():
    logging.basicConfig(
        level=logging.DEBUG, format="%(name)s:[%(levelname)s]: %(message)s"
    )
    c = Client("AF:04:67:EF:19:DA", "92.10.10.25", "55:04:0A:EF:11:CF", 8100)
    receive_thread = threading.Thread(target=c.handle_read)
    receive_thread.start()
    tkinter.mainloop()


if __name__ == "__main__":
    main()

