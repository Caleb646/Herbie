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

from Herbie.Network.Server import SocketServer
from Herbie.Network.Log import write_to_map, State



def car_server_main():
    server = SocketServer()
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
        cv2.namedWindow(mapp_window_name, cv2.WINDOW_NORMAL) # type: ignore
        cv2.resizeWindow(mapp_window_name, default_window_size, default_window_size) # type: ignore
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
                state_updated |= write_to_map(car_map, previous_path, value=(0, 0, 0)) # type: ignore
                state_updated |= write_to_map(car_map, current_path, value=(255, 0, 0)) # type: ignore
                previous_path = current_path
            state_updated |= write_to_map(car_map, obstacles, value=(0, 255, 0)) # type: ignore
            state_updated |= write_to_map(car_map, [position], value=(0, 0, 255)) # type: ignore
            state_updated |= write_to_map(car_map, [target], value=(255, 255, 255)) # type: ignore

            if state_updated:
                current_state.save_current_state(
                    car_map, # type: ignore
                    (
                        ("current_path", current_path), # type: ignore
                        ("obstacles", obstacles),
                        ("xy_position", position), 
                        ("heading", heading),
                        ("target", target)
                    ),
                    "Logs/"
                )

            cv2.imshow(mapp_window_name, car_map) # type: ignore
            if cv2.waitKey(1) & 0xFF == ord('q'): # type: ignore
                break
     
    except Exception as e:
        cv2.destroyAllWindows() # type: ignore
        server.shutdown()
        raise e
    finally:
        cv2.destroyAllWindows() # type: ignore
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
        test_image, # type: ignore
        (
            ("Name", "Testing State"),
            ("distance", 1_000),
            ("position", (100, 100, 100)), # type: ignore
            ("obstacles", [(100, 100, 100), (400, 400, 400)])
        ),
        "Logs"
    )

    state.save_current_state(
        test_image, # type: ignore
        (
            ("Name", "Testing State"),
            ("distance", 1_000),
            ("position", (100, 100, 100)), # type: ignore
            ("obstacles", [(100, 100, 100), (400, 400, 400)])
        ),
        "Logs"
    )

if __name__ == "__main__":
    car_server_main()
    #save_map(test_image)