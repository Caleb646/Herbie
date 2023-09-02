from typing import Union
import math as py_math
import numpy as np

class Math:

    @staticmethod
    def project_point_xy(
        x: int, 
        y: int, 
        angle: float, 
        scaled_distance: int, 
        flip_y=True,
        should_round=False
        ) -> Union[tuple[float, float], tuple[int, int]]:

        flip = -1 if flip_y == True else 1
        rads = py_math.radians(angle)
        proj_x = scaled_distance * py_math.cos(rads) + x
        proj_y = scaled_distance * (flip * py_math.sin(rads)) + y
        if should_round:
            return (round(proj_x), round(proj_y))
        return (proj_x, proj_y)
    
    @staticmethod
    def project_point_tuple(
        position_direction: tuple[int, int, float], 
        scaled_distance: int, 
        flip_y=True,
        should_round=False
        ) -> Union[tuple[float, float], tuple[int, int]]:

        x, y, angle = position_direction
        return Math.project_point_xy(x, y, angle, scaled_distance, flip_y, should_round)

    @staticmethod
    def unsigned_angle(a: tuple[int, int], b: tuple[int, int]) -> float:
        va = np.array(a)
        vb = np.array(b)
        amag = py_math.sqrt(np.dot(va, va))
        bmag = py_math.sqrt(np.dot(vb, vb))
        ab = np.dot(va, vb) / (amag * bmag)
        return py_math.degrees(py_math.acos(ab))

    @staticmethod
    def normalize(vector: tuple[int, int]) -> np.ndarray:
        v = np.array(vector)
        length = py_math.sqrt(np.dot(v, v))
        return v / length

    @staticmethod
    def cross(a: tuple[int, int], b: tuple[int, int]) -> float:
        va: np.ndarray = Math.normalize(a)
        vb: np.ndarray = Math.normalize(b)
        return float(np.cross(va, vb))
    
    @staticmethod
    def calc_turning_angle(
        origin: tuple[int, int, float], 
        target: tuple[int, int], 
        should_round = False
        ) -> float:
        origin_x, origin_y, origin_angle = origin
        origin_dir_x, origin_dir_y = Math.project_point_tuple(
            (0, 0, origin_angle), 
            scaled_distance=1, 
            flip_y=True,
            should_round=True
            )
        target_x, target_y = (target[0] - origin_x, target[1] - origin_y)
        cross_v = -Math.cross((origin_dir_x, origin_dir_y), (target_x, target_y))
        unsigned_angle = Math.unsigned_angle((origin_dir_x, origin_dir_y), (target_x, target_y))
        info = f"Cross: {cross_v} Origin: {origin} Origin Dir: {(origin_dir_x, origin_dir_y)} Target: {target} Trans Target: {(target_x, target_y)} Unsigned Angle: {unsigned_angle}"
        #print(info)
        assert any([round(cross_v) == p for p in [1, 0, -1]]), info
        if cross_v != 0:
            unsigned_angle *= round(cross_v)
        if should_round:
            unsigned_angle = round(unsigned_angle)
        return unsigned_angle
    
    @staticmethod
    def calc_new_heading_from_position(
        origin: tuple[int, int, float], target: tuple[int, int]
        ) -> float:
        """
            current_heading = 0, turning_angle = -90 -> return 270
            current_heading = 90, turning_angle = -90 -> return 0
            current_heading = 270, turning_angle = 90 -> return 0
            current_heading = 270, turning_angle = -90 -> return 180
        """
        _, _, current_heading = origin
        turning_angle = Math.calc_turning_angle(origin, target, should_round=True)
        return Math.calc_new_heading(current_heading, turning_angle)
    
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
        value: Union[int, float], values_to_clamp_to: list[Union[int, float]]
        ) -> Union[int, float]:

        return values_to_clamp_to[np.argmin(np.array(values_to_clamp_to) - value)]
