from typing import Any
import socket
import json


class Client:
    def __init__(self, server_host="192.168.1.35", server_port="8000") -> None:
        self.socket = socket.socket()
        self.server_host = server_host
        self.server_port = server_port
        self.socket.connect((self.server_host, self.server_port))

    def send(self, data: dict[str, Any]):
        result = self.socket.send(json.dumps(data).encode())



if __name__ == "__main__":
    client = Client()
    client.send({"data": [[1], [2], [3]]})