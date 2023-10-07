from typing import Union, Callable, Iterable
import time
import asyncio
import sys
import os
import pathlib

parent = pathlib.Path(os.path.abspath(os.path.curdir))
herbie_path = os.path.join(str(parent))
sys.path.append(herbie_path)

from Herbie.Hardware.Api import DriveTrain, UltraSonic, Camera
from Herbie.Network.Client import Client
from Herbie.CarNav.Api import Car, WebController
from Herbie.Network.Api import WebSocketServer

def soft_reset() -> None:
    from picar_4wd.pin import Pin
    soft_reset_pin = Pin("D16")
    soft_reset_pin.low()
    time.sleep(0.01)
    soft_reset_pin.high()
    time.sleep(0.01)


def car_main(has_server=False):
    soft_reset()
    time.sleep(0.2)
    client = None
    if has_server:
        client = Client()
    try:
        car = Car(
                WebController(
                    DriveTrain(),
                    WebSocketServer(host="192.168.1.36"),
                    camera = Camera()
                ),
                client
            )
        asyncio.run(car.drive_async())
    finally:
        car.shutdown() # type: ignore

if __name__ == "__main__":  
    car_main(has_server=False)

