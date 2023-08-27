import picar_4wd as picar
from picar_4wd.pwm import PWM
from picar_4wd.adc import ADC
from picar_4wd.pin import Pin
from picar_4wd.motor import Motor
from picar_4wd.servo import Servo
from picar_4wd.speed import Speed

import numpy as np

from typing import Union, Callable
import time
import math

def soft_reset() -> None:
    soft_reset_pin = Pin("D16")
    soft_reset_pin.low()
    time.sleep(0.01)
    soft_reset_pin.high()
    time.sleep(0.01)

class DriveTrain:
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
        self.forward(power)
        time.sleep(1)

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
        elif degrees_to < 0: # left
            self._rotate(degrees_to, self.turn_left)
        else: # right
            self._rotate(degrees_to, self.turn_right)
        self.stop()

    def _rotate(self, degrees_to: float, turn_func: Callable[[int], None]) -> None:
        approximate_speed = 25 / 100 # centimeters per second to meters per second
        target_radians = math.radians(abs(degrees_to))
        radius_from_motor_to_center = 11.5 / 100 # centimeters to meters
        time_to_rotate = (target_radians * radius_from_motor_to_center) / approximate_speed # in seconds
        turn_func(2) # start turning
        #print(f"time_to_rotate {time_to_rotate}")
        time.sleep(time_to_rotate + 1 + abs(degrees_to) / 30)

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

    def scan(self, from_degrees: float, to_degrees: float, num_steps: int) -> list[tuple[float, float]]:
        half_steps = num_steps // 2        
        measurements = []

        angle_step = from_degrees // half_steps
        for current_step in range(0, half_steps):
            measurements.append(self.get_distance_at(from_degrees - (angle_step * current_step)))

        angle_step = to_degrees // half_steps    
        for current_step in range(0, half_steps):
            measurements.append(self.get_distance_at(to_degrees - (angle_step * current_step)))

        return measurements
    
class Map:
    def __init__(self, num_rows: int, num_columns: int, cell_size_in_cm: int) -> None:
        self.num_columns = num_columns
        self.num_rows = num_rows
        self.cell_size_in_cm = cell_size_in_cm
        # row = y and column = x
        self._map = np.zeros((self.num_rows, self.num_columns), dtype=np.uint8)

    def is_inbounds(self, x: int, y: int) -> bool:
        if x < 0 or x >= self.num_columns:
            return False
        if y < 0 or y >= self.num_rows:
            return False
        return True

    def get_entry_idx(self, xydir_position: tuple[int, int, float], angle_and_distance: tuple[float, float]) -> tuple[int, int]:
        x, y, car_angle = xydir_position 
        ultra_sonic_angle, raw_distance_in_cm = angle_and_distance
        if raw_distance_in_cm == -1: # -1 = object wasnt found
            return (-1, -1)
        distance = raw_distance_in_cm / self.cell_size_in_cm
        rads = math.radians(car_angle + ultra_sonic_angle) #* -1
        rads = abs(rads)
        entry_x = distance * math.cos(rads) + x
        entry_y = distance * math.sin(rads) + y
        entry_x = round(entry_x)
        entry_y = round(entry_y)
        return (entry_x, entry_y)
    
    def add_entry(self, xydir_position: tuple[int, int, float], angle_and_distance: tuple[float, float]) -> tuple[int, int]:
        x, y = self.get_entry_idx(xydir_position, angle_and_distance)
        # row = y and column = x
        if self.is_inbounds(x, y):
            self._map[y, x] = np.uint8(1)
            return (x, y)
        return (-1, -1)

    def add_entries(self, xydir_position: tuple[int, int, float], ang_distances: list[tuple[float, float]]) -> None:
        for ang_dist in ang_distances:
            self.add_entry(xydir_position, ang_dist)

    def print_map(self) -> None:
        print(self._map)

class Car:
    def __init__(self, drive_train: DriveTrain, ultrasonic: UltraSonic, mapp: Map) -> None:
        self.drive_train = drive_train
        self.ultrasonic = ultrasonic
        self.mapp = mapp
        self.x = self.mapp.num_columns // 2
        self.y = self.mapp.num_rows // 2
        self.heading = 0 # degrees

def test_map():
    num_rows = 11
    num_colums = 11
    cell_size = 10
    mapp = Map(num_rows, num_colums, cell_size)
    # For Servo Degrees
    #   positive degrees = left 
    #   negative degrees = right

    # For Map degrees 
    #   0 = right
    #   270 = down
    #   180 = left
    #   90 = up
    test_entries = [ 
        ((num_rows // 2, num_colums // 2, 0), (0, 30), (8, 5)),
        ((num_rows // 2, num_colums // 2, 0), (-90, 40), (5, 9)),
        ((num_rows // 2, num_colums // 2, 270), (-90, 30), (8, 5)),
        ((num_rows // 2, num_colums // 2, 180), (90, 30), (5, 2)),
        ((num_rows // 2, num_colums // 2, 180), (-90, 30), (5, 8)),
        ((num_rows // 2, num_colums // 2, 90), (90, 30), (2, 5)),
        ((num_rows // 2, num_colums // 2, 90), (-90, 30), (8, 5)),
    ]
    for entry in test_entries:
        position, measurement, obj_positions = entry
        x, y = obj_positions
        tx, ty = mapp.get_entry_idx(position, measurement)
        assert (x, y) == (tx, ty), f"Target: {obj_positions} != Actual: {(tx, ty)}"


if __name__ == "__main__":
    soft_reset()
    time.sleep(0.2)

    test_map()
    try:
        dt = DriveTrain()
        ultra_sonic = UltraSonic(servo_offset = 35)
        mapp = Map(11, 11, 15)
        measurements = ultra_sonic.get_distance_at(0)
        #measurements = ultra_sonic.get_distance_at(65)
        #measurements = ultra_sonic.scan(65, -65, 20)
        #print(measurements)
        #mapp.add_entry((11//2, 11//2, 0), measurements)
        #mapp.add_entries((11//2, 11//2, 0), measurements)
        #mapp.print_map()
        #print(measurements)

        #dt.forward_for(1, 30)
        #dt.rotate(-90)
        #dt.shutdown()
    finally:
        dt.shutdown()

