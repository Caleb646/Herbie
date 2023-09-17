from typing import Any, Generator, Union, Tuple, List
import math as py_math
import numpy as np

from dataclasses import dataclass

@dataclass(frozen=True)
class Position:
    x: Union[int, float]
    y: Union[int, float]
    angle: Union[int, float] = 0

    def __iter__(self):
        attrs = [self.x, self.y, self.angle]
        for attr in attrs:
            yield attr

    def xy_compare(self, other: "Position") -> bool:
        if self.x == other.x and self.y == other.y:
            return True
        return False

    def xy_normalize(self) -> "Position":
        v = self.xy_array()
        length = py_math.sqrt(np.dot(v, v))
        normed = v / length
        return Position(normed[0], normed[1], self.angle)
    
    def xy_tuple(self) -> Tuple[Union[int, float], Union[int, float]]:
        return (self.x, self.y)

    def xy_array(self) -> np.ndarray[Union[int, float], np.dtype]:
        return np.array([self.x, self.y])

    def xy_round(self) -> "Position":
        return Position(round(self.x), round(self.y), self.angle)
    
    def clone(
            self, 
            x: Union[int, float, None] = None, 
            y: Union[int, float, None] = None, 
            angle: Union[float, int, None] = None
            ) -> "Position":
        x_true = x is not None
        y_true = y is not None
        angle_true = angle is not None
        if x_true and y_true and angle_true:
            return Position(x, y, angle)
        if x_true and y_true:
            return Position(x, y, self.angle)
        if angle_true:
            return Position(self.x, self.y, angle)  
        return Position(self.x, self.y, self.angle) 
    
class Math:

    @staticmethod
    def project_position(
        pos: Position, 
        scaled_distance: float, 
        flip_y=True,
        should_round=False
        ) -> Position:

        flip = -1 if flip_y == True else 1
        rads = py_math.radians(pos.angle)  
        proj_pos = pos.clone(
            scaled_distance * py_math.cos(rads) + pos.x, 
            scaled_distance * (flip * py_math.sin(rads)) + pos.y
            )
        #print(pos, proj_pos, scaled_distance)
        if should_round:
            return proj_pos.xy_round()
        return proj_pos
    
    @staticmethod
    def unsigned_angle(a: Position, b: Position) -> float:
        va = a.xy_array()
        vb = b.xy_array()
        amag = py_math.sqrt(np.dot(va, va))
        bmag = py_math.sqrt(np.dot(vb, vb))
        ab = np.dot(va, vb) / (amag * bmag)
        return py_math.degrees(py_math.acos(ab))

    @staticmethod
    def cross(a: Position, b: Position) -> float:
        va: np.ndarray = a.xy_normalize().xy_array()
        vb: np.ndarray = b.xy_normalize().xy_array()
        return float(np.cross(va, vb))
    
    @staticmethod
    def calc_turning_angle(
        origin: Position, 
        target: Position, 
        should_round = False
        ) -> float:
        origin_dir = Math.project_position(
            origin.clone(0, 0), 
            scaled_distance=1, 
            flip_y=True,
            should_round=True
            )
        translated_target = target.clone(target.x - origin.x, target.y - origin.y)
        cross_v = -round(Math.cross(origin_dir, translated_target))
        unsigned_angle = Math.unsigned_angle(origin_dir, translated_target)
        info = f"Cross: {cross_v} Origin: {origin} Origin Dir: {origin_dir} Target: {target} Trans Target: {translated_target} Unsigned Angle: {unsigned_angle}"
        #print(info)
        assert any([cross_v == p for p in [1, 0, -1]]), info
        if cross_v != 0:
            unsigned_angle *= cross_v
        if should_round:
            unsigned_angle = round(unsigned_angle)
        return unsigned_angle
    
    @staticmethod
    def calc_new_heading_from_position(
        origin: Position, target: Position
        ) -> float:
        """
            current_heading = 0, turning_angle = -90 -> return 270
            current_heading = 90, turning_angle = -90 -> return 0
            current_heading = 270, turning_angle = 90 -> return 0
            current_heading = 270, turning_angle = -90 -> return 180
        """
        turning_angle = Math.calc_turning_angle(origin, target, should_round=True)
        return Math.calc_new_heading(origin.angle, turning_angle)
    
    @staticmethod
    def calc_new_heading(current_heading: float, turning_angle: float) -> float:
        """
            current_heading = 0, turning_angle = -90 -> return 270
            current_heading = 90, turning_angle = -90 -> return 0
            current_heading = 270, turning_angle = 90 -> return 0
            current_heading = 270, turning_angle = -90 -> return 180
        """
        current_heading += turning_angle
        if current_heading < 0:
            current_heading = 360 - abs(current_heading)
        return round(current_heading) % 360

    @staticmethod
    def closest_to(
        value: Union[int, float], values_to_clamp_to: List[Union[int, float]]
        ) -> Union[int, float]:

        return values_to_clamp_to[np.argmin(np.array(values_to_clamp_to) - value)]
