from typing import Any
import socket
import json
import pickle
import time
import numpy as np


class Client:
    def __init__(self, server_host="192.168.1.35", server_port=8000) -> None:
        self.socket = socket.socket()
        self.server_host = server_host
        self.server_port = server_port
        self.socket.settimeout(0.5)
        self.socket.connect((self.server_host, self.server_port))
        
    def send(self, data: dict[str, Any]): 
        encoded_data = json.dumps(data).encode()
        try:
            self.socket.sendall(encoded_data)
        except ConnectionResetError:
            self.socket.connect((self.server_host, self.server_port))
            self.socket.sendall(encoded_data)

    def shutdown(self):
        self.socket.shutdown()
        self.socket.close()


if __name__ == "__main__":
    client = Client()
    while True:
        client.send({"data": [[1], [2], [3]] })
        time.sleep(1)