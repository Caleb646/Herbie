from typing import Union, Callable, Iterable
import time
import asyncio
import sys
import os
import pathlib

parent = pathlib.Path(os.path.abspath(os.path.curdir))
herbie_path = os.path.join(str(parent))
sys.path.append(herbie_path)

from Herbie.Hardware.DriveTrain import MockDriveTrain
from Herbie.Network.Client import Client
from Herbie.CarNav.Api import Car, WebController
from Herbie.Network.Api import WebSocketServer


def car_main(has_server=False):
    client = None
    if has_server:
        client = Client()
    try:
        car = Car(
                WebController(
                    MockDriveTrain(),
                    WebSocketServer(),
                    sleep_per_step=0.01
                ),
                client
            )
        asyncio.run(car.drive_async(), debug=True)
    finally:
        car.shutdown() # type: ignore

if __name__ == "__main__":  
    car_main(has_server=False)

