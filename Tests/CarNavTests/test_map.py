from typing import List, Tuple, Union
from Herbie.CarNav.Mapp import Mapp
from Herbie.CMath.Api import Math, Position
from Tests.utils import *

def test_map():
    num_rows = 11
    num_colums = 11
    cell_size = 10
    mapp = Mapp(num_rows, num_colums, cell_size)
    # For Servo Degrees
    #   positive degrees = left 
    #   negative degrees = right

    # For Map degrees from the perspective of a Numpy Array 
    #   0 = right
    #   270 = down
    #   180 = left
    #   90 = up

    test_entries: List[Tuple[Position, Tuple[int, int], Tuple[int, int]]] = [ 
        (Position(num_rows // 2, num_colums // 2, 0), (0, 30), (8, 5)), # x, y
        (Position(num_rows // 2, num_colums // 2, 0), (SERVO_LOOK_LEFT, 30), (5, 2)),
        (Position(num_rows // 2, num_colums // 2, 0), (SERVO_LOOK_RIGHT, 30), (5, 8)),

        (Position(num_rows // 2, num_colums // 2, 270), (SERVO_LOOK_RIGHT, 30), (2, 5)),
        (Position(num_rows // 2, num_colums // 2, 270), (SERVO_LOOK_LEFT, 30), (8, 5)),

        (Position(num_rows // 2, num_colums // 2, 180), (SERVO_LOOK_LEFT, 30), (5, 8)),
        (Position(num_rows // 2, num_colums // 2, 180), (SERVO_LOOK_RIGHT, 30), (5, 2)),

        (Position(num_rows // 2, num_colums // 2, 90), (SERVO_LOOK_LEFT, 30), (2, 5)),
        (Position(num_rows // 2, num_colums // 2, 90), (SERVO_LOOK_RIGHT, 30), (8, 5)),
    ]
    for i, entry in enumerate(test_entries):
        car_position, sensor_measurement, projected_obstacle_position = entry
        x, y = projected_obstacle_position
        target_pos: Position = mapp.get_obstacle_idx(car_position, sensor_measurement)
        assert (x, y) == target_pos.xy_tuple(), f"Entry: {i} Target: {projected_obstacle_position} != Actual: {target_pos} -> Car Pos {car_position} Servo Angle {sensor_measurement}"