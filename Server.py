import os
from typing import Any, Tuple, Union, List, Iterable
from dataclasses import dataclass
import socket
import json
import cv2
import numpy as np
import numpy.typing as npt
import select
import time


class Server:
    CLOSING_MESSAGE = "CLOSING_SOCKET"
    def __init__(self, host=socket.gethostbyname(socket.gethostname()), port=8000) -> None:
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host
        self.port = port

    def run(self) -> Iterable[dict[str, Any]]:
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
                        if decoded_data == Server.CLOSING_MESSAGE:
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

def get_local_time() -> str:
    return time.strftime('%b_%A_%I_%M_%S', time.localtime())

@dataclass
class State:
    State_ID_Type = str
    State_Values_Type = Union[str, int, float, Tuple[int, int], List[Tuple[int, int, float]]]
    State_Type = Tuple[ Tuple[State_ID_Type, State_Values_Type], ... ]
    current_step: int = 0
    state_sub_dir: str = get_local_time()
    def save_current_state(
            self,
            mapp: npt.NDArray[np.uint8],
            state: State_Type, 
            main_dir: str,
            filename = f"State_{get_local_time()}",
            new_img_width = 1_000,
            new_img_height = 1_000
            ) -> bool:
        
        main_sub_dir = os.path.join(main_dir, self.state_sub_dir)
        filepath_without_ext = os.path.join(main_sub_dir, f"{filename}_{self.current_step}")
        if not os.path.isdir(main_sub_dir):
            os.mkdir(main_sub_dir)
        resized = cv2.resize(
            mapp, (new_img_width, new_img_height), interpolation = cv2.INTER_NEAREST
            )
        log_file_path =f"{filepath_without_ext}.txt"
        map_path = f"{filepath_without_ext}.jpeg"
        with open(log_file_path, "w") as f:
            lines: List[str] = [f"current_time -> {get_local_time()}"]
            for name, item in state:
                lines.append(f"\n{name} -> {str(item)}")
            f.writelines(lines)
        self.current_step += 1
        return cv2.imwrite(map_path, resized)
    
    def reset(self) -> None:
        self.current_step = 0
        self.state_sub_dir = get_local_time()

def write_to_map(
        mapp: npt.NDArray[np.uint8], 
        objects: list[tuple[int, int]], 
        value: tuple[np.uint8, np.uint8, np.uint8]
        ) -> bool:
    map_changed = False
    for obj in objects:
        if len(obj) == 2:
            x, y = obj
            mapp[y, x] = value
            map_changed = True   
    return map_changed

def car_server_main():
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
        current_state = State()
        cv2.namedWindow(mapp_window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(mapp_window_name, default_window_size, default_window_size)
        for connection_ended, data in server.run():
            map_size = data.get("map_size", None)
            cell_size = data.get("cell_size", cell_size)
            current_path: list[Tuple[int, int]] = data.get("current_path", [])
            obstacles: list[Tuple[int, int]] = data.get("obstacles", [])
            position: Tuple[int, int] = data.get("position", ())
            heading: float = data.get("heading", -1)
            target: Tuple[int, int] = data.get("target", ())
            state_updated = False
            if connection_ended:
                car_map = np.zeros(car_map.shape)
                current_state.reset()
            # resize car map if dimensions are given
            if map_size and car_map.shape != (map_size, map_size, 3):
                print(f"Resizing map to: {(map_size, map_size, 3)}")
                car_map = np.zeros((map_size, map_size, 3))
            if current_path:
                state_updated |= write_to_map(car_map, previous_path, value=(0, 0, 0))
                state_updated |= write_to_map(car_map, current_path, value=(255, 0, 0))
                previous_path = current_path
            state_updated |= write_to_map(car_map, obstacles, value=(0, 255, 0))
            state_updated |= write_to_map(car_map, [position], value=(0, 0, 255))
            state_updated |= write_to_map(car_map, [target], value=(255, 255, 255))

            if state_updated:
                current_state.save_current_state(
                    car_map,
                    (
                        ("current_path", current_path),
                        ("obstacles", obstacles),
                        ("xy_position", position),
                        ("heading", heading),
                        ("target", target)
                    ),
                    "Logs/"
                )

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


def test_state():
    test_image = np.zeros((50, 50, 3))
    #test_image[15:25, 15:25] = (255, 255, 255)
    test_image[16, 24] = (0, 0, 255)
    test_image[16, 23] = (0, 0, 255)
    test_image[16, 22] = (0, 0, 255)
    test_image[16, 21] = (0, 0, 255)
    test_image[16, 20] = (0, 0, 255)
    test_image[50//2, 50//2] = (255, 255, 255)

    state = (
        "Testing State",
        1_000,
    )

    state = State()
    state.save_current_state(
        test_image,
        (
            ("Name", "Testing State"),
            ("distance", 1_000),
            ("position", (100, 100, 100)),
            ("obstacles", [(100, 100, 100), (400, 400, 400)])
        ),
        "Logs"
    )

    state.save_current_state(
        test_image,
        (
            ("Name", "Testing State"),
            ("distance", 1_000),
            ("position", (100, 100, 100)),
            ("obstacles", [(100, 100, 100), (400, 400, 400)])
        ),
        "Logs"
    )


if __name__ == "__main__":
    car_server_main()
    #save_map(test_image)
        