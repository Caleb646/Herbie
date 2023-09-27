import os
from typing import Any, Tuple, Union, List, Iterable
from dataclasses import dataclass
import socket
import json
import select
import time

import asyncio
from websockets.server import serve
from websockets.sync.client import connect



class SocketServer:
    CLOSING_MESSAGE = "CLOSING_SOCKET"
    def __init__(self, host=socket.gethostbyname(socket.gethostname()), port=8000) -> None:
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host
        self.port = port

    def run(self) -> Iterable[Tuple[bool, dict[str, Any]]]:
        print(f"Binding host at IP address: {self.host} and Port: {self.port}")
        self.socket.bind((self.host, self.port))
        self.socket.listen()
        # add self.socket to connections 
        # so we know when to a connection is waiting to be accepted
        connections = [self.socket]
        timeout = 0.1
        while True:
            # select.select returns a subset of ready to ready, write, and exceptional conditions sockets
            readable, writable, errored = select.select(connections, [], [], timeout)
            for socket in readable:
                if socket is self.socket:
                    client_socket, address = self.socket.accept()
                    client_socket.setblocking(False)
                    connections.append(client_socket)
                    print(f"Incoming connection: {address}")
                else:
                    data: bytes = socket.recv(2048)
                    if data:
                        decoded_data = data.decode()
                        if decoded_data == SocketServer.CLOSING_MESSAGE:
                            print(f"Removing Connection: {socket.getpeername()}")
                            socket.close()
                            connections.remove(socket)
                            yield True, {}
                        else:
                            yield False, json.loads(data.decode())
                    # when a client socket is succesfully shutdown and then closed
                    # it will send a recieve of 0 bytes. So this connection can be removed
            yield False, {}

    def shutdown(self):
        self.socket.close()


class WebSocketServer:
    def __init__(self, host=socket.gethostbyname(socket.gethostname()), port=8000) -> None:
        self.host = host
        self.port = port

    async def send(self, ws):
        async for message in ws:
            pass

    async def recv(self, ws):
        while True:
            await asyncio.sleep(2.0)
            await ws.send("data")

    async def handle(self, ws):
        consumer_task = asyncio.create_task(self.recv(ws))
        producer_task = asyncio.create_task(self.send(ws))
        done, pending = await asyncio.wait(
            [consumer_task, producer_task],
            return_when=asyncio.FIRST_COMPLETED,
        )
        for task in pending:
            task.cancel()

    async def run(self):
        async with serve(lambda ws : self.handle(ws), self.host, self.port):
            await asyncio.Future()  # run forever


if __name__ == "__main__":
    server = WebSocketServer("localhost")
    asyncio.run(server.run())