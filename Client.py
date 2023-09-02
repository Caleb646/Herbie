from typing import Any
import socket
import json
import time


class Client:
    def __init__(self, server_host="192.168.1.35", server_port=8000) -> None:
        self.socket = socket.socket()
        self.server_host = server_host
        self.server_port = server_port
        self.socket.settimeout(0.5)
        self.is_connected = False
        #self.socket.connect((self.server_host, self.server_port))

    def connect(self) -> "Client":
        try:
            self.socket.connect((self.server_host, self.server_port))
            self.is_connected = True
        except ConnectionError as e:
            print(f"FAILED to connect to server {(self.server_host, self.server_port)} because: {str(e)}")
            self.is_connected = False
        return self
        
    def send(self, data: dict[str, Any]): 
        if self.is_connected:
            encoded_data = json.dumps(data).encode()
            try:
                self.socket.sendall(encoded_data)
            except ConnectionResetError:
                self.connect()
                self.socket.sendall(encoded_data)
        else:
            print("Error can NOT send data on a socket that has no connection")

    def shutdown(self):
        if self.is_connected:
            self.socket.shutdown(socket.SHUT_RDWR)
            self.socket.close()


if __name__ == "__main__":
    client = Client()
    while True:
        client.send({"data": [[1], [2], [3]] })
        time.sleep(1)