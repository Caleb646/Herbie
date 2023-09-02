from typing import Any, Iterable
import socket
import json
import pickle
import cv2
import numpy as np
import numpy.typing as npt

import threading
import pickle


class Server:
    def __init__(self, host="192.168.1.35", port=8000) -> None:
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connections: dict[str, socket.socket] = {}
        self.host = host
        self.port = port

    def run(self) -> Iterable[dict[str, Any]]:
        self.socket.bind((self.host, self.port))
        self.socket.listen()
        conn, addr = self.socket.accept()
        conn.settimeout(20)
        print(f"Connected to: {addr}")
        while True:
            data = conn.recv(2048)
            if data:
                yield json.loads(data.decode())
            yield {}

def write_to_map(
        mapp: npt.NDArray[np.uint8], 
        objects: list[tuple[int, int]], 
        value: tuple[np.uint8, np.uint8, np.uint8]
        ):
    
    for obj in objects:
        if len(obj) == 2:
            x, y = obj
            mapp[y, x] = value

def run_map_window(mapp, default_window_size=500):
    mapp_window_name = 'Mapp_Panel'
    cv2.namedWindow(mapp_window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(mapp_window_name, default_window_size, default_window_size)
    while True:
        cv2.imshow(mapp_window_name, mapp)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cv2.destroyAllWindows()


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
    cv2_thread = threading.Thread(target=run_map_window, args=(car_map, default_map_size))
    cv2_thread.start()

    #for data in test_data:
    for data in server.run():
        map_size = data.get("map_size", map_size)
        cell_size = data.get("cell_size", cell_size)
        current_path: list[tuple[int, int]] = data.get("current_path", [])
        obstacles: list[tuple[int, int]] = data.get("obstacles", [])
        position: tuple[int, int] = data.get("position", ())
        heading: float = data.get("heading", -1)
        target: tuple = data.get("target", ())

        if current_path:
            write_to_map(car_map, previous_path, value=(0, 0, 0))
            write_to_map(car_map, current_path, value=(255, 0, 0))
            previous_path = current_path
        write_to_map(car_map, obstacles, value=(0, 255, 0))
        write_to_map(car_map, [position], value=(0, 0, 255))
        write_to_map(car_map, [target], value=(255, 255, 255))

    cv2_thread.join()