from typing import Union, Callable, Iterable
import time

# importing this way will include the picar package
from Herbie.Hardware.Api import DriveTrain, UltraSonic, Camera
from Herbie.Network.Client import Client
from Herbie.CarNav.Api import Car, AutonomousController, TFDetector
from Herbie.CMath.Api import Position

def soft_reset() -> None:
    from picar_4wd.pin import Pin
    soft_reset_pin = Pin("D16")
    soft_reset_pin.low()
    time.sleep(0.01)
    soft_reset_pin.high()
    time.sleep(0.01)


def car_main(dist_x, dist_y, map_size=51, cell_size=15, servo_offset=35, has_server=False):
    soft_reset()
    time.sleep(0.2)
    client = None
    if has_server:
        client = Client()
    try:
        car = Car(
                AutonomousController(
                    map_size,
                    cell_size,
                    Position(map_size // 2 + dist_x, map_size // 2 + dist_y),
                    DriveTrain(),
                    UltraSonic(servo_offset=servo_offset),
                    TFDetector(Camera())
                ),
                client
            )
        car.drive()
    finally:
        car.shutdown() # type: ignore

if __name__ == "__main__":  
    car_main(dist_x=6, dist_y=3, cell_size=25, has_server=True)

