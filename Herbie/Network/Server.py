import os
from typing import Any, Dict, Tuple, Union, List, Iterable
from dataclasses import dataclass
import socket
import json
import select
import time

import asyncio
from collections import deque
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
        self.connections_ = set()
        self.messages_: deque[Dict[str, Any]] = deque()

    async def send(self, message: Dict[str, Any]):
        encoded_data = json.dumps(message)
        for ws in self.connections_:
            await ws.send(encoded_data)

    def get_message(self) -> Dict[str, Any]:
        if self.messages_:
            return self.messages_.popleft()
        return {}

    async def recv_(self, ws):
        async for message in ws:
            print(f"Received Message: {message}")
            decoded_data = message
            if isinstance(message, bytes):
                decoded_data = message.decode()
            self.messages_.append(json.loads(decoded_data))
            await asyncio.sleep(0.01)

    async def handle(self, ws):
        self.connections_.add(ws)
        print(f"Adding Connection: {ws}")
        consumer_task = asyncio.create_task(self.recv_(ws))
        done, pending = await asyncio.wait(
            [consumer_task],
            return_when=asyncio.FIRST_COMPLETED,
        )
        for task in pending:
            task.cancel()

    async def run(self):
        async with serve(lambda ws : self.handle(ws), self.host, self.port):
            print(f"Serving at: ws://{self.host}:{self.port}")
            await asyncio.Future()  # run forever


if __name__ == "__main__":
    server1 = WebSocketServer("localhost", 8080)
    #server2 = WebSocketServer("localhost", 8000)
    asyncio.run(server1.run())