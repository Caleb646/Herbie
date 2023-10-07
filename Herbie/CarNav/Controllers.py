
from Herbie.Hardware.Base import BaseSensor, BaseCamera, BaseDriveTrain
from Herbie.CarNav.Pathfinder import Pathfinder
from Herbie.CarNav.Mapp import Mapp
from Herbie.CarNav.Base import BaseController, BaseDetector
from Herbie.CMath.Api import Math, Position

from typing import Any, AsyncGenerator, Generator, List, Tuple, Dict, Union
import time
import asyncio
from collections import deque
import numpy as np

class AutonomousController(BaseController):
    def __init__(
            self,
            map_size: int,
            cell_size: int, 
            target: Position,
            drive_train: BaseDriveTrain,
            obstacle_sensor: BaseSensor, 
            detector: Union[BaseDetector, None] = None
            ):
        super(AutonomousController, self).__init__(drive_train)
        self.obstacle_sensor_ = obstacle_sensor
        self.detector_ = detector
        self.mapp_ = Mapp(map_size, map_size, cell_size)
        self.pathfinder_ = Pathfinder()
        self.car_position: Position = Position(
            self.mapp_.num_columns // 2, self.mapp_.num_rows // 2, angle=0
        )
        self.target_ = target
        self.current_path_: deque[Position] = deque()
        self.seen_objects_: Dict[str, bool] = {"stop sign" : False}

    def drive(self) -> Generator[bool, None, bool]: # Generator[YieldType, SendType, ReturnType]
        while self.car_position.xy_compare(self.target_):
            self.scan_update_path_()
            self.see_objects_()
            if self.current_path_:
                reached_next_cell = self.step(self.current_path_.popleft())
            yield True
        return True
    
    def step(self, new_position: Position) -> bool:
        angle_to_turn = Math.calc_turning_angle(self.car_position, new_position)
        if abs(angle_to_turn) > 0:
            self.turn_(angle_to_turn)
            self.car_position = Math.calc_updated_heading(self.car_position, angle_to_turn)
            if self.scan_update_path_():
                return False
        self.move_forward_(self.mapp_.cell_size_in_cm)
        self.car_position = Math.calc_new_xy_position(self.car_position, self.mapp_.cell_size_in_cm)
        return True
    
    def shutdown(self) -> None:
        self.drive_train_.shutdown()
    
    def get_log_data(self) -> Dict[str, Any]:
        return {
            "map_size": self.mapp_.num_columns,
            "cell_size": self.mapp_.cell_size_in_cm,
            "target": self.target_,
            "position": self.car_position,
            "obstacles": self.mapp_.get_obstacles(),
            "current_path": self.current_path_
        }
 
    def see_objects_(self):
        if self.detector_:
            detector_results = [self.detector_.detect().get_object_score("stop sign") > 0.5 for _ in range(2)]
            if sum(detector_results) > 1 and not self.seen_objects_["stop sign"]:
                print("Found stop sign")
                self.seen_objects_["stop sign"] = True
                time.sleep(3.0)
    
    def scan_update_path_(self) -> bool:
        obstacles = [self.obstacle_sensor_.get_distance_at(0)]
        if self.mapp_.add_obstacles(self.car_position, obstacles):
            self.current_path_ = deque(
                # Position at index 0 is the current position of the car
                self.pathfinder_.a_star(self.mapp_, self.car_position, self.target_)[1:]
                )
            return True
        return False
    

class WebController(BaseController):

    def __init__(
            self, 
            drive_train: BaseDriveTrain, 
            server,
            sleep_per_step = 0.05, 
            camera: Union[BaseCamera, None] = None,
            sensor: Union[BaseSensor, None] = None
            ):
        super(WebController, self).__init__(drive_train)
        self.sleep_per_step_ = sleep_per_step
        self.server_ = server
        self.camera_ = camera
        self.sensor_ = sensor
        self.go_ = {
            "forward": False,
            "backward": False,
            "turn_left": False,
            "turn_right": False
        }

    async def drive(self) -> None: #AsyncGenerator[bool, None]: # Generator[YieldType, SendType, ReturnType]
        run_server = asyncio.create_task(self.server_.run())
        driving = asyncio.create_task(self.drive_())
        done, pending = await asyncio.wait(
            [run_server, driving],
            return_when=asyncio.FIRST_COMPLETED
        )
        for task in pending:
            task.cancel()

    async def drive_(self):
        while True:
            message: Dict[str, Any] = self.server_.get_message()
            if message:
                self.go_ = message
                successful = self.step()
            await self.server_.send(self.get_log_data())
            await asyncio.sleep(self.sleep_per_step_)

    def step(self) -> bool:
        assert sum(self.go_.values()) <= 1, f"{self.go_}"
        if self.go_["forward"]:
            self.drive_train_.forward(power=50)
        elif self.go_["backward"]:
            self.drive_train_.backward(power=50)
        elif self.go_["turn_left"]:
            self.drive_train_.turn_left(power=50)
        elif self.go_["turn_right"]:
            self.drive_train_.turn_right(power=50)
        else:
            self.drive_train_.stop()
        return True

    def shutdown(self) -> None:
        self.drive_train_.shutdown()
    
    def get_log_data(self) -> Dict[str, Any]:
        camera_image = np.zeros((320, 320, 3), dtype=np.uint8)
        alphas = np.ones((320, 320, 1), dtype=np.uint8) * 255
        if self.camera_ and self.camera_.is_camera_available():
            status, camera_image = self.camera_.see()
        obstacle = (-1, -1)
        if self.sensor_:
            obstacle = self.sensor_.get_distance_at(0)
        return {
<<<<<<< HEAD
            "speed": self.drive_train_.get_avg_speed,
            "image": np.concatenate([camera_image, alphas], axis=2).flatten().astype(np.uint8).tolist(),
=======
            "speed": round(self.drive_train_.get_avg_speed, 1),
            "image": np.concatenate([camera_image, alphas], axis=2).flatten().tolist(),
>>>>>>> d9a6e531b23bdd17c3b7764cc3b7cae7981c9bb7
            "obstacle": obstacle
        }