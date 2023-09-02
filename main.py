from picar_4wd.pwm import PWM
from picar_4wd.pin import Pin
from picar_4wd.servo import Servo

from typing import Union, Callable
from copy import deepcopy
import numpy as np
import time

from DriveTrain import DriveTrain
from Mapp import Mapp
from Math import Math
from Pathfinder import Pathfinder
from Client import Client
import test

def soft_reset() -> None:
    soft_reset_pin = Pin("D16")
    soft_reset_pin.low()
    time.sleep(0.01)
    soft_reset_pin.high()
    time.sleep(0.01)


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

class Car:
    LEFT_TURN = 90
    RIGHT_TURN = -90
    OPPOSITE_TURN = 180

    def __init__(self, drive_train: DriveTrain, ultrasonic: UltraSonic, mapp: Mapp, has_server: bool = True) -> None:
        self.drive_train = drive_train
        self.ultrasonic = ultrasonic
        self.mapp = mapp
        self.pathfinder = Pathfinder()
        self.x = self.mapp.num_columns // 2
        self.y = self.mapp.num_rows // 2
        self.heading = 0 # degrees
        self.client = Client()
        self.has_server = has_server
        if self.has_server:
            self.client.connect()
        self.current_path = []
        self.target = ()

    def drive(self, target: tuple[int, int]):
        self._scan_and_update_map()  
        path = self.pathfinder.a_star(self.mapp, self.current_position, target)
        self.current_path = path
        self.target = target
        # path[0] is the current position of the car
        current_path_idx = 1
        self.print_path_trace(path)
        try:
            self.send_server_data()
            while self.xy_position != target:
                if current_path_idx > len(path):
                    print(f"Invalid Path Idx: {current_path_idx} and Map:\n {self.mapp._map}")
                    break           
                should_update_path = self._move_to(path[current_path_idx])
                current_path_idx += 1
                if should_update_path:
                    path = self.pathfinder.a_star(self.mapp, self.current_position, target)
                    #self.print_path_trace(path)
                    self.current_path = path
                    self.send_server_data()
                    current_path_idx = 1
        except Exception as e:
            self.shutdown()
            raise e

    def _move_to(self, target: tuple[int, int]) -> bool:
        angle_to_turn = Math.calc_turning_angle(self.current_position, target)
        #print(f"Proj: {(dirx, diry)} Targ {(target_x, target_y)} Heading: {self.heading}", angle, cross)
        if abs(angle_to_turn) < 1: # forward
            self._move_forward(self.mapp.cell_size_in_cm)
        else:
            self._turn(angle_to_turn)
        return self._scan_and_update_map()

    def _move_forward(self, distance) -> bool:
        self.drive_train.forward_for(30, self.mapp.cell_size_in_cm)
        dirx, diry = self.get_direction_vector(distance / self.mapp.cell_size_in_cm)
        dirx = round(dirx)
        diry = round(diry)
        # dirx and diry should be either 0, 1, or -1
        #assert abs(dirx + diry) == 1, f"Moving with Invalid Direction {(dirx, diry)}"
        self.x += dirx  
        self.y += diry
        return True

    def _turn(self, degrees_to: float) -> None:
        self.drive_train.rotate(degrees_to)
        self.heading += degrees_to
        if self.heading < 0:
            self.heading = 360 - abs(self.heading)
        self.heading %= 360
        print(self.heading)

    def _scan_and_update_map(self) -> bool:
        return self.mapp.add_obstacles(
            self.current_position, self.ultrasonic.scan(65, -65, 7)
            )

    def print_position(self) -> None:
        x, y, _ = self.current_position
        temp = self.mapp._map[y, x]
        self.mapp._map[y, x] = 2
        print(self.mapp._map)
        self.mapp._map[y, x] = temp

    def print_path_trace(self, path: list[tuple[int, int]]) -> None:
        copied_map: np.ndarray = deepcopy(self.mapp._map)
        start_marker = 2
        for i, (x, y) in enumerate(path):
            copied_map[y, x] = start_marker + i
        print("Path Trace:\n", copied_map)

    def send_server_data(self):
        if self.has_server:
            data = {
                "map_size": self.mapp.num_columns,
                "cell_size": self.mapp.cell_size_in_cm,
                "obstacles": self.mapp.get_obstacles(),
                "position": self.xy_position,
                "heading" : self.heading,
                "current_path": self.current_path,
                "target": self.target
            }
            self.client.send(data)
    
    def shutdown(self) -> None:
        self.drive_train.shutdown()
        self.client.shutdown()

    @property
    def current_position(self) -> tuple[int, int, float]:
        return (self.x, self.y, self.heading)
    
    @property
    def xy_position(self) -> tuple[int, int]:
        return (self.x, self.y)
    
    def get_direction_vector(self, scaled_distance=1) -> tuple[int, int]:
        return Math.project_point_tuple(
            (0, 0, self.heading), 
            scaled_distance, 
            flip_y=True
            )

def car_main(map_size=51, cell_size=15, servo_offset=35, has_server=False):
    soft_reset()
    time.sleep(0.2)
    try:
        car = Car(
            DriveTrain(), 
            UltraSonic(servo_offset = servo_offset), 
            Mapp(map_size, map_size, cell_size),
            has_server=has_server
            )
        car.drive((car.x + 1, car.y))
        #car._turn(-90)
    finally:
        car.shutdown()

if __name__ == "__main__":
    
    #test.test_main()
    #test.test_new_heading()
    #test.test_pathfinding()
    car_main()

