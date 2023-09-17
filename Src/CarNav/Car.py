from Hardware.Base import BaseCamera, BaseDriveTrain, BaseSensor
from Network.Client import Client
from Mapp import Mapp
from CMath import Math, Position
from Pathfinder import Pathfinder

from typing import List, Tuple, Union, Iterable
import time

class Car:
    LEFT_TURN = 90
    RIGHT_TURN = -90
    OPPOSITE_TURN = 180

    def __init__(
            self, 
            drive_train: BaseDriveTrain, 
            ultrasonic: BaseSensor,
            camera: BaseCamera, 
            mapp: Mapp, 
            has_server: bool = False
            ) -> None:
        
        self.drive_train = drive_train
        self.ultrasonic = ultrasonic
        self.mapp = mapp
        self.pathfinder = Pathfinder()
        self.position = Position(
            self.mapp.num_columns // 2, self.mapp.num_rows // 2, angle=0
        )
        self.client = Client()
        self.camera = camera
        self.has_server = has_server
        if self.has_server:
            self.client.connect()
        self.current_path: List[Position] = []
        self.target = ()

    def drive(self, target: Position):
        self._scan_and_update_map()  
        self.current_path = self.pathfinder.a_star(self.mapp, self.position, target)
        self.target = target
        # path[0] is the current position of the car
        current_path_idx = 1
        found = False
        try:
            self.send_server_data()
            while not self.position.xy_compare(target):
                time.sleep(0.1)
                camera_results = [self.camera.see().has_object("stop sign") > 0.5 for _ in range(2)]
                if sum(camera_results) > 1 and not found:
                    print("Found stop sign")
                    found = True
                    time.sleep(3.0)
                if current_path_idx > len(self.current_path) - 1:
                    print(f"Invalid Path Idx: {current_path_idx} and Map:\n {self.mapp._map}")
                    break           
                should_update_path = self._move_to(self.current_path[current_path_idx])
                current_path_idx += 1
                if should_update_path:
                    self.current_path = self.pathfinder.a_star(self.mapp, self.position, target)
                    print(self.current_path)
                    self.send_server_data()
                    current_path_idx = 1
        except Exception as e:
            self.shutdown()
            raise e

    def _move_to(self, target: Position) -> bool:
        angle_to_turn = Math.calc_turning_angle(self.position, target)
        print(self.position, target, angle_to_turn)
        if abs(angle_to_turn) < 1: # forward
            self._move_forward(self.mapp.cell_size_in_cm)
        else:
            self._turn(angle_to_turn)
            self._move_forward(self.mapp.cell_size_in_cm)
        return self._scan_and_update_map()

    def _move_forward(self, distance) -> bool:
        self.drive_train.forward_for(30, self.mapp.cell_size_in_cm)
        self.position = self.get_direction_vector(distance / self.mapp.cell_size_in_cm).xy_round()
        return True

    def _turn(self, turning_angle: float) -> None:
        self.drive_train.rotate(turning_angle)
        self.position = self.position.clone(
            angle=Math.calc_new_heading(self.position.angle, turning_angle)
            )

    def _scan_and_update_map(self) -> bool:
        # return self.mapp.add_obstacles(
        #     self.current_position, self.ultrasonic.scan(2, -2, 1, samples_per_step=2)
        #     )
        return self.mapp.add_obstacles(
            self.position, [self.ultrasonic.get_distance_at(0)]
            )

    def send_server_data(self):
        if self.has_server:
            data = {
                "map_size": self.mapp.num_columns,
                "cell_size": self.mapp.cell_size_in_cm,
                "obstacles": self.mapp.get_obstacles(),
                "position": self.position,
                "current_path": self.current_path,
                "target": self.target
            }
            self.client.send(data)
    
    def shutdown(self) -> None:
        self.drive_train.shutdown()
        self.client.shutdown()
    
    def get_direction_vector(self, scaled_distance: Union[int, float] = 1) -> Position:
        return Math.project_position(
            self.position.clone(0, 0), 
            scaled_distance, 
            flip_y=True
            )