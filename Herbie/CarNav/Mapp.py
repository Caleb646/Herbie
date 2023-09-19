from typing import List, Tuple, Union, Iterable, Generator
import numpy as np
from Herbie.CMath.Api import Math, Position

class Mapp:
    OBSTACLE_NOTFOUND = -1
    OBSTACLE_ID = 1

    def __init__(
            self, 
            num_rows: int, 
            num_columns: int, 
            cell_size_in_cm: int
            ) -> None:
        
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
    
    def is_open(self, x: int, y: int) -> bool:
        return self._map[y, x] != Mapp.OBSTACLE_ID
    
    def get_open_neighbors(self, x, y) -> Iterable[Position]:
        offsets: List[Tuple[int, int]] = [
            (x + 1, y), 
            (x - 1, y), 
            (x, y + 1), 
            (x, y - 1),
            # diagonal neighbors
            (x + 1, y + 1),
            (x - 1, y - 1),
            (x - 1, y + 1),
            (x + 1, y - 1)
        ]
        for x, y in offsets:
            if self.is_inbounds(x, y) and self.is_open(x, y): # not a block
                yield Position(x, y)

    def get_obstacle_idx(
            self, 
            car_position: Position, 
            angle_and_distance: tuple[float, float]
            ) -> Position:
        
        ultra_sonic_angle, raw_distance_in_cm = angle_and_distance
        if raw_distance_in_cm == Mapp.OBSTACLE_NOTFOUND: # -1 = object wasnt found
            return Position(-1, -1)
        proj_position = Math.project_position(
            car_position.clone(angle=car_position.angle + ultra_sonic_angle),
            raw_distance_in_cm / float(self.cell_size_in_cm),
            flip_y = True
        )
        return proj_position.xy_round()
    
    def add_obstacle(
            self, 
            car_position: Position, 
            angle_and_distance: tuple[float, float]
            ) -> bool:
        
        map_position = self.get_obstacle_idx(
            car_position, angle_and_distance
            )
        return self.add_obstacle_xy(map_position.xy_tuple()) # type: ignore
    
    def add_obstacle_xy(self, obstacle_xy: tuple[int, int]) -> bool:       
        x, y = obstacle_xy
        # row = y and column = x
        if self.is_inbounds(x, y) and self.is_open(x, y):
            self._map[y, x] = Mapp.OBSTACLE_ID
            return True
        return False

    def add_obstacles(
            self, 
            car_position: Position, 
            angles_distances: list[tuple[float, float]]
            ) -> bool:
        
        found_new_obstacle = False
        for ang_dist in angles_distances:
            found_new_obstacle |= self.add_obstacle(car_position, ang_dist)
        return found_new_obstacle
    
    def add_obstacles_xy(self, obstacle_xys: list[tuple[int, int]]) -> bool:     
        added_obstacle = False
        for xy in obstacle_xys:
            added_obstacle |= self.add_obstacle_xy(xy)
        return added_obstacle
    
    def get_obstacles(self) -> list[tuple[int, int]]:
        obstacles = []
        for y in range(self.num_rows):
            for x in range(self.num_columns):
                if not self.is_open(x, y):
                    obstacles.append((x, y))
        return obstacles