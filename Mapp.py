import numpy as np
from Math import Math

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
    
    def get_open_neighbors(self, x, y) -> tuple[int, int]:
        offsets = ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1))
        for x, y in offsets:
            if self.is_inbounds(x, y) and self.is_open(x, y): # not a block
                yield (x, y)

    def get_obstacle_idx(
            self, 
            xydir_position: tuple[int, int, float], 
            angle_and_distance: tuple[float, float]
            ) -> tuple[int, int]:
        
        x, y, car_angle = xydir_position 
        ultra_sonic_angle, raw_distance_in_cm = angle_and_distance
        if raw_distance_in_cm == Mapp.OBSTACLE_NOTFOUND: # -1 = object wasnt found
            return (-1, -1)
        return Math.project_point_xy(
            x, 
            y, 
            car_angle + ultra_sonic_angle, 
            raw_distance_in_cm / self.cell_size_in_cm,
            flip_y = True,
            should_round = True
            )
    
    def add_obstacle(
            self, 
            xydir_position: tuple[int, int, float], 
            angle_and_distance: tuple[float, float]
            ) -> bool:
        
        x, y = self.get_obstacle_idx(
            xydir_position, angle_and_distance
            )
        # row = y and column = x
        if self.is_inbounds(x, y) and self.is_open(x, y):
            self._map[y, x] = Mapp.OBSTACLE_ID
            return True
        return False

    def add_obstacles(
            self, 
            xydir_position: tuple[int, int, float], 
            angles_distances: list[tuple[float, float]]
            ) -> bool:
        
        found_new_obstacle = False
        for ang_dist in angles_distances:
            found_new_obstacle |= self.add_obstacle(xydir_position, ang_dist)
        return found_new_obstacle
    
    def get_obstacles(self) -> list[tuple[int, int]]:
        obstacles = []
        for y in range(self.num_rows):
            for x in range(self.num_columns):
                if not self.is_open(y, x):
                    obstacles.append((x, y))
        return obstacles

    def print_map(self) -> None:
        print(self._map)