from typing import Union, Callable, Iterable
import time

# importing this way will include the picar package
from Hardware.api import DriveTrain, UltraSonic, Camera
from CarNav.api import Car, Mapp
from CMath.api import Position
import Tests.test as test

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
    try:
        car = Car(
            DriveTrain(), 
            UltraSonic(servo_offset = servo_offset), 
            Camera(),
            Mapp(map_size, map_size, cell_size),
            has_server=has_server
            )
        car.drive(Position(car.position.x + dist_x, car.position.y + dist_y))
        #car._turn(-90)
    finally:
        car.shutdown() # type: ignore

if __name__ == "__main__":
    
    #test.test_main()
    #test.test_turning_angle()
    #test.test_calc_new_heading()
    #test.test_pathfinding()
    #car_main(has_server=True)
    car_main(dist_x=6, dist_y=3, cell_size=25, has_server=True)
    #car_main(dist_x=10, dist_y=0, cell_size=25, has_server=True)

    #us = UltraSonic(35)
    #us.scan(-65, 65, 10)

