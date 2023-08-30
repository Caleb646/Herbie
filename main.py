import picar_4wd as picar
from picar_4wd.pwm import PWM
from picar_4wd.adc import ADC
from picar_4wd.pin import Pin
from picar_4wd.motor import Motor
from picar_4wd.servo import Servo
from picar_4wd.speed import Speed

import numpy as np

from typing import Union, Callable
from queue import PriorityQueue
from copy import deepcopy
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
        starting_speed = 30 # cm
        time_to_move = centimeters / starting_speed
        self.forward(power)
        step = 0.1
        num_steps = time_to_move // step
        max_steps = 100
        while num_steps > 0 and max_steps > 0: 
            time.sleep(step)
            current_speed = (self.get_left_rear_speed + self.get_right_rear_speed) / 2
            expected_distance_travelled = starting_speed * step
            actual_distance_travelled = current_speed * step
            missed_step = (expected_distance_travelled - actual_distance_travelled) / expected_distance_travelled
            num_steps += missed_step - 1
            max_steps -= 1
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
        starting_speed = 5 / 100 # centimeters per second to meters per second
        target_radians = math.radians(abs(degrees_to))
        radius_from_motor_to_center = 11.5 / 100 # centimeters to meters
        time_to_rotate = (target_radians * radius_from_motor_to_center) / starting_speed # in seconds
        turn_func(30) # start turning
        #time_to_sleep = time_to_rotate + 0.5 + abs(degrees_to) / 30
        step = 0.01
        num_steps = time_to_rotate // step
        max_steps = 1000
        while num_steps > 0 and max_steps > 0: 
            time.sleep(step)
            current_speed = min(self.get_left_rear_speed, self.get_right_rear_speed) / 100
            if current_speed < starting_speed - 2 / 100:
                num_steps += 1
            elif current_speed > starting_speed + 2 / 100:
                num_steps -= 1
            num_steps -= 1
            max_steps -= 1

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
    
    def get_open_neighbors(self, x, y) -> tuple[int, int]:
        offsets = ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1))
        for x, y in offsets:
            if self.is_inbounds(x, y) and self._map[y, x] != 1: # not a block
                yield (x, y)

    def get_entry_idx(self, xydir_position: tuple[int, int, float], angle_and_distance: tuple[float, float]) -> tuple[int, int]:
        x, y, car_angle = xydir_position 
        ultra_sonic_angle, raw_distance_in_cm = angle_and_distance
        if raw_distance_in_cm == -1: # -1 = object wasnt found
            return (-1, -1)
        distance = raw_distance_in_cm / self.cell_size_in_cm
        rads = math.radians(car_angle + ultra_sonic_angle)
        entry_x = distance * math.cos(rads) + x
        entry_y = distance * -math.sin(rads) + y
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

    def has_entry(self, xydir_position: tuple[int, int, float], angle_and_distance: tuple[float, float]) -> bool:
        x, y = self.get_entry_idx(xydir_position, angle_and_distance)
        if self.is_inbounds(x, y) and self._map[y, x] == 1:
            return True
        for nx, ny in self.get_neighbors(x, y):
            if self._map[ny, nx] == 1:
                return True
        return False
    
    def to_one_d(self, point: tuple[int, int]) -> int:
        x, y = point
        return y * self.num_rows + x

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

    def drive(self, target: tuple[int, int]):
        self._scan_and_update_map()  
        #self.print_path_trace(path)
        max_steps = 1_000
        path = self.a_star(target)
        # path[0] is the current position of the car
        current_path_idx = 1
        self.print_path_trace(path)
        while self.current_position[0:2] != target and max_steps > 0:           
            should_update_path = self._move_to(path[current_path_idx])
            current_path_idx += 1
            print(should_update_path, current_path_idx)
            if should_update_path:
                path = self.a_star(target)
                self.print_path_trace(path)
                current_path_idx = 1
            max_steps -= 1

    def _move_to(self, point: tuple[int, int]) -> bool:
        x, y, heading = self.current_position
        target_x, target_y = point
        assert (abs(x - target_x) + abs(y - target_y)) == 1,\
        f"Current: {(x, y)} -> Target: {(target_x, target_y)} must be within 1 cell of each other"
        if x - target_x == -1: # forward
            self._move_forward(self.mapp.cell_size_in_cm)
        elif x - target_x == 1: # backward
            self._turn(180)
        elif y - target_y == -1: # turn right
            self._turn(90)
        else: # turn left
            self._turn(-90)
        return self._scan_and_update_map()

    def _move_forward(self, distance):
        self.drive_train.forward_for(30, self.mapp.cell_size_in_cm)
        scaled_distance = distance / self.mapp.cell_size_in_cm
        self.x += int(math.cos(math.radians(self.heading)) * scaled_distance)
        # y has to be flipped because array starts in the top left
        self.y += int(-math.sin(math.radians(self.heading)) * scaled_distance)

    def print_position(self):
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
        print(copied_map)
    
    def shutdown(self):
        self.drive_train.shutdown()

    def a_star(self, target: tuple[int, int]) -> list[tuple[int, int]]:
        num_rows = self.mapp.num_rows
        class Node:
            def __init__(self, x: int, y:int, prev_node: Union["Node", None] = None) -> None:
                self.x = x
                self.y = y
                self.prev_node = prev_node
                self.hscore = 0
                self.gscore = 0
                self.fscore = 0

            def __eq__(self, onode: "Node") -> bool:
                return (self.x == onode.x and self.y == onode.y)

            def __gt__(self, other: "Node") -> bool:
                return (self.fscore > other.fscore)
            
            def __lt__(self, other: "Node") -> bool:
                return not (self.fscore > other.fscore or self.fscore == other.fscore)
            
            def calc_scores(self, current_node: "Node", target_node: "Node") -> "Node":
                self.hscore = self.get_distance(target_node)
                self.gscore = current_node.gscore + self.get_distance(current_node)
                self.fscore = self.gscore + self.hscore
                return self

            def get_distance(self, target_node: "Node") -> int:
                return (self.x - target_node.x)**2 + (self.y - target_node.y)**2

            @property
            def key(self) -> int:
                return self.y * num_rows + self.x

        def find_path(end_node: Node) -> list[tuple[int, int]]:
            path = [(end_node.x, end_node.y)]
            current_node = end_node.prev_node
            while current_node:
                path.append((current_node.x, current_node.y))
                current_node = current_node.prev_node
            path.reverse()
            return path

        target_node = Node(target[0], target[1])
        start_x, start_y, _ = self.current_position
        starting_node = Node(start_x, start_y)
        
        # x, y, f, g, h
        # g = current.g + distance(neighbor, current)
        # h = distance(current, target)
        # f = g + h
        open_list = PriorityQueue()
        open_list.put((0, starting_node))
        open_set = {starting_node.key : 0.0}
        closed_set = set()
        #self.print_position()
        while open_list.not_empty:
            priority, current_node = open_list.get()
            if current_node == target_node:
                return find_path(current_node)
            closed_set.add(current_node.key)
            for neig_x, neig_y in self.mapp.get_open_neighbors(current_node.x, current_node.y):
                neigh_node = Node(neig_x, neig_y, current_node).calc_scores(current_node, target_node)
                if neigh_node.key in closed_set:
                    continue  
                existing_gscore = open_set.get(neigh_node.key, None)
                if existing_gscore and neigh_node.gscore > existing_gscore:
                        continue
                open_list.put((neigh_node.fscore, neigh_node))
                open_set[neigh_node.key] = neigh_node.gscore
        return []

    @property
    def current_position(self) -> tuple[int, int, float]:
        return (self.x, self.y, self.heading)
    
    def _scan_and_update_map(self) -> bool:
        objects = self.ultrasonic.scan(65, -65, 15)
        self.mapp.add_entries(self.current_position, objects)
        return len(objects) > 0

    def _turn(self, degrees_to: float) -> None:
        self.drive_train.rotate(degrees_to)
        self.heading += degrees_to

def test_map():
    num_rows = 11
    num_colums = 11
    cell_size = 10
    mapp = Map(num_rows, num_colums, cell_size)
    # For Servo Degrees
    #   positive degrees = left 
    #   negative degrees = right

    # For Map degrees from the perspective of a Numpy Array 
    #   0 = right
    #   270 = down
    #   180 = left
    #   90 = up
    LOOK_LEFT = 90 # Servo Look Left
    LOOK_RIGHT = -90 # Servo Look Right
    test_entries = [ 
        ((num_rows // 2, num_colums // 2, 0), (0, 30), (8, 5)), # x, y
        ((num_rows // 2, num_colums // 2, 0), (LOOK_LEFT, 30), (5, 2)),
        ((num_rows // 2, num_colums // 2, 0), (LOOK_RIGHT, 30), (5, 8)),

        ((num_rows // 2, num_colums // 2, 270), (LOOK_RIGHT, 30), (2, 5)),
        ((num_rows // 2, num_colums // 2, 270), (LOOK_LEFT, 30), (8, 5)),

        ((num_rows // 2, num_colums // 2, 180), (LOOK_LEFT, 30), (5, 8)),
        ((num_rows // 2, num_colums // 2, 180), (LOOK_RIGHT, 30), (5, 2)),

        ((num_rows // 2, num_colums // 2, 90), (LOOK_LEFT, 30), (2, 5)),
        ((num_rows // 2, num_colums // 2, 90), (LOOK_RIGHT, 30), (8, 5)),
    ]
    for entry in test_entries:
        position, measurement, obj_positions = entry
        x, y = obj_positions
        tx, ty = mapp.get_entry_idx(position, measurement)
        assert (x, y) == (tx, ty), f"Target: {obj_positions} != Actual: {(tx, ty)} -> Car Pos {position} Servo Angle {measurement}"

def test_ultrasonic():
    us = UltraSonic(servo_offset = 35)
    for i in range(1, 10):
        print(us.get_distance_at(0), us.get_distance_at(5))

def test_drive_train():
    dt = DriveTrain()
    start_time = time.time()
    dt.rotate(-45)
    dt.shutdown()
    return time.time() - start_time

if __name__ == "__main__":
    soft_reset()
    time.sleep(0.2)
    #test_map()
    #test_ultrasonic()
    #test_drive_train()
    try:
        car = Car(
            DriveTrain(), 
            UltraSonic(servo_offset = 35), 
            Map(11, 11, 15)
            )
        car.drive((6, 5))
    finally:
        car.shutdown()

