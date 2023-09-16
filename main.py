from picar_4wd.pwm import PWM
from picar_4wd.pin import Pin
from picar_4wd.servo import Servo

from typing import Union, Callable, Iterable
from copy import deepcopy
import numpy as np
import time

from DriveTrain import DriveTrain
from Mapp import Mapp
from Math import Math
from Pathfinder import Pathfinder
from Client import Client
from UltraSonic import UltraSonic
from Camera import Camera, CameraResult
import test

def soft_reset() -> None:
    soft_reset_pin = Pin("D16")
    soft_reset_pin.low()
    time.sleep(0.01)
    soft_reset_pin.high()
    time.sleep(0.01)


class Car:
    LEFT_TURN = 90
    RIGHT_TURN = -90
    OPPOSITE_TURN = 180

    def __init__(
            self, 
            drive_train: DriveTrain, 
            ultrasonic: UltraSonic, 
            mapp: Mapp, 
            has_server: bool = False
            ) -> None:
        
        self.drive_train = drive_train
        self.ultrasonic = ultrasonic
        self.mapp = mapp
        self.pathfinder = Pathfinder()
        self.x = self.mapp.num_columns // 2
        self.y = self.mapp.num_rows // 2
        self.heading = 0 # degrees
        self.client = Client()
        self.camera = Camera()
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
        camera_gen: Iterable[CameraResult] = self.camera.see()
        found = False
        try:
            #print(path)
            self.send_server_data()
            while self.xy_position != target:
                time.sleep(0.1)
                camera_results = [next(camera_gen).has_object("stop sign") > 0.5 for _ in range(2)]
                if sum(camera_results) > 1 and not found:
                    print("Found stop sign")
                    found = True
                    time.sleep(3.0)
                if current_path_idx > len(path) - 1:
                    print(f"Invalid Path Idx: {current_path_idx} and Map:\n {self.mapp._map}")
                    break           
                should_update_path = self._move_to(path[current_path_idx])
                current_path_idx += 1
                if should_update_path:
                    path = self.pathfinder.a_star(self.mapp, self.current_position, target)
                    print(path)
                    self.current_path = path
                    self.send_server_data()
                    current_path_idx = 1
        except Exception as e:
            self.shutdown()
            raise e

    def _move_to(self, target: tuple[int, int]) -> bool:
        #print(self.current_position, self.target)
        angle_to_turn = Math.calc_turning_angle(self.current_position, target)
        print(self.current_position, target, angle_to_turn)
        if abs(angle_to_turn) < 1: # forward
            self._move_forward(self.mapp.cell_size_in_cm)
        else:
            self._turn(angle_to_turn)
            self._move_forward(self.mapp.cell_size_in_cm)
        return self._scan_and_update_map()

    def _move_forward(self, distance) -> bool:
        self.drive_train.forward_for(30, self.mapp.cell_size_in_cm)
        dirx, diry = self.get_direction_vector(distance / self.mapp.cell_size_in_cm)
        dirx = round(dirx)
        diry = round(diry)
        self.x += dirx  
        self.y += diry
        return True

    def _turn(self, turning_angle: float) -> None:
        self.drive_train.rotate(turning_angle)
        self.heading = Math.calc_new_heading(self.heading, turning_angle)

    def _scan_and_update_map(self) -> bool:
        # return self.mapp.add_obstacles(
        #     self.current_position, self.ultrasonic.scan(2, -2, 1, samples_per_step=2)
        #     )
        return self.mapp.add_obstacles(
            self.current_position, [self.ultrasonic.get_distance_at(0)]
            )

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

def car_main(dist_x, dist_y, map_size=51, cell_size=15, servo_offset=35, has_server=False):
    soft_reset()
    time.sleep(0.2)
    try:
        car = Car(
            DriveTrain(), 
            UltraSonic(servo_offset = servo_offset), 
            Mapp(map_size, map_size, cell_size),
            has_server=has_server
            )
        car.drive((car.x + dist_x, car.y + dist_y))
        #car._turn(-90)
    finally:
        car.shutdown()

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

