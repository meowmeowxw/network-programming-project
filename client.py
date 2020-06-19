#!/usr/bin/env python3

import asyncore
import logging
import socket
import tkinter
from common import *


class Client(asyncore.dispatcher):
    def __init__(self, mac_client: str, ip_client: str) -> None:
        asyncore.dispatcher.__init__(self)
        self.logger = logging.getLogger("Client {Client.ip_client}")

        self.mac_client = Mac(mac_client)
        self.ip_client = IP(ip_client)
        self.ip_server = IP("195.1.10.10")
        self.mac_gateway = Mac("55:04:0A:EF:11:CF")
        self.server = ("localhost", 8000)
        self.default_gateway = ("localhost", 8100)

        self.window = tkinter.Tk()
        self.window.after_idle(poll_asyncore_once)
        self.window.title(f"{self.ip_client.ip}")
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
            self.window, text="Invio", command=self.send_message
        )
        # integriamo il tasto nel pacchetto
        send_button.pack()

        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect(self.default_gateway)
        self.data_to_write = [b"online"]

    def handle_connect(self):
        pass

    def handle_close(self):
        self.close()

    def handle_read(self):
        self.recv(4096)

    def writable(self):
        return bool(self.data_to_write)

    def handle_write(self):
        data = self.data_to_write.pop()
        hdr = self.__build_header()
        sent = self.send(hdr + data)
        if sent < len(data):
            remaining = data[sent:]
            self.data_to_write.append(remaining)
        self.logger.debug(f"handle_write() -> {sent}: {data[:sent].rstrip()}")

    def send_message(self):
        self.data_to_write.append(self.message.get().encode())

    def __build_header(self):
        return header.build(
            dict(
                mac_src=self.mac_client.mac,
                mac_dst=self.mac_gateway.mac,
                ip_src=self.ip_client.ip,
                ip_dst=self.ip_server.ip,
            )
        )


def poll_asyncore_once():
    asyncore.loop(count=1)


def main():
    logging.basicConfig(
        level=logging.DEBUG, format="%(name)s:[%(levelname)s]: %(message)s"
    )
    Client("32:04:0A:EF:19:CF", "92.10.10.15")
    print("ciaooo")
    tkinter.mainloop()


if __name__ == "__main__":
    main()

