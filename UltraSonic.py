from picar_4wd.pwm import PWM
from picar_4wd.pin import Pin
from picar_4wd.servo import Servo

from typing import Union, Callable
import numpy as np
import time

class UltraSonic:
    MAX_DISTANCE = 400 # 400 centimeters is the max range of the sensor
    ANGLE_RANGE = 180
    STEP = 18

    def __init__(self, servo_offset: int, timeout: float = 0.01):
        self.servo_offset = int(servo_offset)
        self.timeout = timeout
        self.trig = Pin("D8")
        self.echo = Pin("D9")
        self.servo = Servo(PWM("P0"), offset=self.servo_offset)
        self.current_angle = 0
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
    
    def get_distance_at(self, degrees_to: float) -> tuple[float, float]:
        self.servo.set_angle(degrees_to)
        time.sleep(0.1)
        self.current_angle = degrees_to
        return (degrees_to, self.get_distance())

    def scan(
            self, from_degrees: float, to_degrees: float, num_steps: int, samples_per_step: int = 2
            ) -> list[tuple[float, float]]:
        half_steps = num_steps // 2 
        #        
        step_size = from_degrees // half_steps
        from_angles = [from_degrees - (i * step_size) for i in range(half_steps)]
        #
        step_size = to_degrees // half_steps
        to_angles = [to_degrees - (i * step_size) for i in range(half_steps)]
        #
        all_angles = sorted(from_angles + to_angles + [0])
        measurements = []
        for angle in all_angles:
            angle_center, distance_center = self.get_distance_at(angle)
            samples = [distance_center]
            sample_size = 20 // samples_per_step
            for i in range(1, (samples_per_step // 2) + 1):
                _, d = self.get_distance_at(angle - sample_size * i)
                samples.append(d)
            for i in range(1, (samples_per_step // 2) + 1):
                _, d = self.get_distance_at(angle + sample_size * i)
                samples.append(d)
            if samples.count(-1) > len(samples) // 2:
                continue
                #print(f"Object with distance samples {samples} and angle: {angle_center} was determined to be noise.")
            else:
                filtered_samples = list(filter(lambda dist : dist != -1, samples))
                measurements.append([angle_center, sum(filtered_samples) / len(filtered_samples)])
        return measurements