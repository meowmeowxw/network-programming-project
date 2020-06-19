#!/usr/bin/env python3

import asyncore
import logging
import socket
import tkinter
from common import *


class Client:
    def __init__(self, mac_client: str, ip_client: str) -> None:
        self.mac_client = Mac(mac_client)
        self.ip_client = IP(ip_client)
        self.ip_server = IP("195.1.10.10")
        self.mac_gateway = Mac("55:04:0A:EF:11:CF")
        self.server = ("localhost", 8000)
        self.default_gateway = ("localhost", 8100)

        self.logger = logging.getLogger(f"Client {self.ip_client} ")

        self.window = tkinter.Tk()
        self.window.title(f"{self.ip_client}")
        self.messages_frame = tkinter.Frame(self.window)
        self.message = tkinter.StringVar()
        self.message.set("Write here your message")
        self.scrollbar = tkinter.Scrollbar(self.messages_frame)
        self.msg_list = tkinter.Listbox(
            self.messages_frame, height=15, width=50, yscrollcommand=self.scrollbar.set
        )
        self.scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
        self.msg_list.pack(side=tkinter.LEFT, fill=tkinter.BOTH)
        self.msg_list.pack()
        self.messages_frame.pack()
        self.entry_field = tkinter.Entry(self.window, textvariable=self.message)
        # leghiamo la funzione send al tasto Return
        self.entry_field.bind("<Return>", self.send_message)

        self.entry_field.pack()
        # creiamo il tasto invio e lo associamo alla funzione send
        send_button = tkinter.Button(
            self.window, text="Send", command=self.send_message
        )
        # integriamo il tasto nel pacchetto
        send_button.pack()

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
                self.msg_list.insert(tkinter.END, data)
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
        self.data_to_write.append(self.message.get().encode())
        self.handle_write()

    def __build_header(self):
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
    Client("32:04:0A:EF:19:CF", "92.10.10.15")
    tkinter.mainloop()


if __name__ == "__main__":
    main()

