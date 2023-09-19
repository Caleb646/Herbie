from picar_4wd.pwm import PWM
from picar_4wd.pin import Pin
from picar_4wd.motor import Motor
from picar_4wd.speed import Speed

from Herbie.Hardware.Base import BaseDriveTrain

from typing import Union, Callable
import time
import math


def block_for(
        time_to_block, starting_speed, sample_speed_func, step=0.01, max_steps=1000
        ) -> None:
    num_steps = time_to_block / step
    while num_steps > 0 and max_steps > 0: 
        time.sleep(step)
        current_speed = sample_speed_func()
        expected_distance_travelled = starting_speed * step
        actual_distance_travelled = current_speed * step
        missed_step = (expected_distance_travelled - actual_distance_travelled) / expected_distance_travelled
        num_steps += missed_step - 1
        max_steps -= 1

class DriveTrain(BaseDriveTrain):
    def __init__(self):
        self.left_front = Motor(PWM("P13"), Pin("D4"), is_reversed=False) # motor 1
        self.right_front = Motor(PWM("P12"), Pin("D5"), is_reversed=False) # motor 2
        self.left_rear = Motor(PWM("P8"), Pin("D11"), is_reversed=False) # motor 3
        self.right_rear = Motor(PWM("P9"), Pin("D15"), is_reversed=False) # motor 4

        self.left_rear_speed = Speed(pin=25)
        self.right_rear_speed = Speed(pin=4)    
   
        self.left_rear_speed.start()
        self.right_rear_speed.start()

        self.stop()

    def stop(self) -> None:
        self.left_front.set_power(0)
        self.left_rear.set_power(0)
        self.right_front.set_power(0)
        self.right_rear.set_power(0)

    def forward_for(self, power: int, centimeters: float) -> None:
        starting_speed = 30 # cm
        self.forward(power)
        block_for(
            centimeters / starting_speed, 
            starting_speed, 
            lambda : self.get_avg_speed, 
            step=0.01, 
            max_steps=200
            )
        self.stop()

    def forward(self, power: int) -> None:
        self.left_front.set_power(power)
        self.left_rear.set_power(power)
        self.right_front.set_power(power)
        self.right_rear.set_power(power)

    def backward(self, power: int) -> None:
        self.left_front.set_power(-power)
        self.left_rear.set_power(-power)
        self.right_front.set_power(-power)
        self.right_rear.set_power(-power)

    def turn_left(self, power: int) -> None:
        self.left_front.set_power(-power)
        self.left_rear.set_power(-power)
        self.right_front.set_power(power)
        self.right_rear.set_power(power)

    def turn_right(self, power: int) -> None:
        self.left_front.set_power(power)
        self.left_rear.set_power(power)
        self.right_front.set_power(-power)
        self.right_rear.set_power(-power)

    def rotate(self, degrees_to: float):
        self.stop()
        if degrees_to == 0:
            return
        elif degrees_to < 0:    # right
            self._rotate(degrees_to, self.turn_right)
        else:                   # left
            self._rotate(degrees_to, self.turn_left)
        self.stop()

    def _rotate(self, degrees_to: float, turn_func: Callable[[int], None]) -> None:
        starting_speed = 35 / 100 # centimeters per second to meters per second
        target_radians = math.radians(abs(degrees_to))
        radius_from_motor_to_center = 11.5 / 100 # centimeters to meters
        time_to_rotate = (target_radians * radius_from_motor_to_center) / starting_speed # in seconds
        turn_func(60) # start turning
        block_for(
            time_to_rotate, 
            starting_speed, 
            lambda : self.get_avg_speed / 100, 
            step=0.01, 
            max_steps=1_000
            )

    def shutdown(self) -> None:
        self.stop()
        self.left_rear_speed.deinit()
        self.right_rear_speed.deinit()

    @property
    def get_left_rear_speed(self) -> Union[int, float]: # speed in centimeters per second
        return self.left_rear_speed()
    @property
    def get_right_rear_speed(self) -> Union[int, float]: # speed in centimeters per second
        return self.right_rear_speed()
    @property
    def get_avg_speed(self) -> float:
        return (self.get_left_rear_speed + self.get_right_rear_speed) / 2.0