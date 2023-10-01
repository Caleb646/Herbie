from Herbie.Hardware.Base import BaseSensor

from typing import Union, Callable
import numpy as np
import time

class UltraSonic(BaseSensor):
    MAX_DISTANCE = 400 # 400 centimeters is the max range of the sensor
    ANGLE_RANGE = 180
    STEP = 18

    def __init__(self, servo_offset: int, timeout: float = 0.01):
        from picar_4wd.pwm import PWM
        from picar_4wd.pin import Pin
        from picar_4wd.servo import Servo
        self.servo_offset = int(servo_offset)
        self.timeout = timeout
        self.trig = Pin("D8")
        self.echo = Pin("D9")
        self.servo = Servo(PWM("P0"), offset=self.servo_offset)
        self.max_angle = self.ANGLE_RANGE / 2
        self.min_angle = -self.ANGLE_RANGE / 2

    def get_distance(self) -> float:
        self.trig.low()
        time.sleep(0.01)
        self.trig.high()
        time.sleep(0.000015)
        self.trig.low()
        pulse_end = 0
        pulse_start = 0
        timeout_start = time.time()
        while self.echo.value() == 0:
            pulse_start = time.time()
            if pulse_start - timeout_start > self.timeout:
                return -1
        while self.echo.value() == 1:
            pulse_end = time.time()
            if pulse_end - timeout_start > self.timeout:
                return -1
                #return -2
        during = pulse_end - pulse_start
        # 340 = the speed of sound is 343.4 m/s or 0.0343 cm / microsecond
        dist = round(during * 340 / 2 * 100, 2) # in centimeters
        if dist > self.MAX_DISTANCE:
            return -1
        return dist
    
    def move_sensor_to(self, angle: float) -> bool:
        self.servo.set_angle(angle)
        time.sleep(0.1)
        return True

    def shutdown(self) -> None:
        pass