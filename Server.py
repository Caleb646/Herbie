from typing import Any, Iterable
import socket
import json
import cv2
import numpy as np
import numpy.typing as npt
import select
import time


class Server:
    CLOSING_MESSAGE = "CLOSING_SOCKET"
    def __init__(self, host="192.168.1.35", port=8000) -> None:
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host
        self.port = port

    def run(self) -> Iterable[dict[str, Any]]:
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
                        if decoded_data == Server.CLOSING_MESSAGE:
                            print(f"Removing Connection: {socket.getpeername()}")
                            socket.close()
                            connections.remove(socket)
                        else:
                            yield json.loads(data.decode())
                    # when a client socket is succesfully shutdown and then closed
                    # it will send a recieve of 0 bytes. So this connection can be removed
            yield {}

    def shutdown(self):
        self.socket.close()

def write_to_map(
        mapp: npt.NDArray[np.uint8], 
        objects: list[tuple[int, int]], 
        value: tuple[np.uint8, np.uint8, np.uint8]
        ):
    
    for obj in objects:
        if len(obj) == 2:
            x, y = obj
            mapp[y, x] = value

if __name__ == "__main__":
    server = Server()
    map_size = None
    cell_size = None
    previous_path = []
    default_map_size = 100
    car_map = np.zeros((default_map_size, default_map_size, 3), dtype=np.uint8)
    test_data = [{
        "map_size": 200,
        "cell_size": 15,
        "current_path": [(i, j) for i in range(default_map_size//2) for j in range(default_map_size//2)],
        "obstacle": [(25, 25), (26, 25), (27, 28), (30, 30)]
    }]

    try:
        default_window_size = 500
        mapp_window_name = 'Mapp_Panel'
        cv2.namedWindow(mapp_window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(mapp_window_name, default_window_size, default_window_size)
        #for data in test_data:
        for data in server.run():
            map_size = data.get("map_size", None)
            cell_size = data.get("cell_size", cell_size)
            current_path: list[tuple[int, int]] = data.get("current_path", [])
            obstacles: list[tuple[int, int]] = data.get("obstacles", [])
            position: tuple[int, int] = data.get("position", ())
            heading: float = data.get("heading", -1)
            target: tuple = data.get("target", ())
            # resize car map if dimensions are given
            if map_size and car_map.shape != (map_size, map_size, 3):
                print(f"Resizing map to: {(map_size, map_size, 3)}")
                car_map = np.zeros((map_size, map_size, 3))
            if current_path:
                write_to_map(car_map, previous_path, value=(0, 0, 0))
                write_to_map(car_map, current_path, value=(255, 0, 0))
                previous_path = current_path
            write_to_map(car_map, obstacles, value=(0, 255, 0))
            write_to_map(car_map, [position], value=(0, 0, 255))
            write_to_map(car_map, [target], value=(255, 255, 255))

            cv2.imshow(mapp_window_name, car_map)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
     
    except Exception as e:
        cv2.destroyAllWindows()
        server.shutdown()
        raise e
    finally:
        cv2.destroyAllWindows()
        server.shutdown()
        