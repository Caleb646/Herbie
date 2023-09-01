from typing import Any
from collections import Mapping
import socket
import json


class Server:
    def __init__(self, host="192.168.1.35", port="8000") -> None:
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connections: Mapping[str, socket.socket] = {}
        self.host = host
        self.port = port

    def run(self) -> Mapping[str, Any]:
        self.socket.bind((self.host, self.port))
        self.socket.listen(1)
        conn, addr = self.socket.accept()
        while True:
            yield json.loads(conn.recv(2048).decode())



if __name__ == "__main__":
    server = Server()
    for data in server.run():
        print(data)