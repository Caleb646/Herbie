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
        tx, ty = mapp.get_obstacle_idx(position, measurement)
        assert (x, y) == (tx, ty), f"Target: {obj_positions} != Actual: {(tx, ty)} -> Car Pos {position} Servo Angle {measurement}"

def test_turning_angle():
    TURN_LEFT = 90
    TURN_RIGHT = -90

    LOOKING_UP = 90
    LOOKING_DOWN = 270
    LOOKING_RIGHT = 0
    LOOKING_LEFT = 180

    current_and_new = [
        [(5, 5, LOOKING_RIGHT), (6, 5), 0],
        [(5, 5, LOOKING_RIGHT), (5, 6), TURN_RIGHT],
        [(5, 5, LOOKING_RIGHT), (5, 4), TURN_LEFT],
        [(5, 5, LOOKING_RIGHT), (4, 5), 180],

        [(5, 5, LOOKING_UP), (5, 6), 180],
        [(5, 5, LOOKING_UP), (5, 4), 0],
        [(5, 5, LOOKING_UP), (6, 5), TURN_RIGHT],
        [(5, 5, LOOKING_UP), (4, 5), TURN_LEFT],

        [(5, 5, LOOKING_LEFT), (5, 6), TURN_LEFT],
        [(5, 5, LOOKING_LEFT), (5, 4), TURN_RIGHT],
        [(5, 5, LOOKING_LEFT), (4, 5), 0],
        [(5, 5, LOOKING_LEFT), (6, 5), 180],

        [(5, 5, LOOKING_DOWN), (6, 5), TURN_LEFT],
        [(5, 5, LOOKING_DOWN), (4, 5), TURN_RIGHT],
        [(5, 5, LOOKING_DOWN), (5, 6), 0],
        [(5, 5, LOOKING_DOWN), (5, 4), 180],
    ]

    for current_pos, target_xy, expected_new_heading in current_and_new:
        new_heading = Math.calc_turning_angle(current_pos, target_xy)
        assert expected_new_heading == new_heading, f"Current: {current_pos} Target: {target_xy} New: {new_heading} != Expected {expected_new_heading}"

def test_drive_train():
    dt = DriveTrain()
    start_time = time.time()
    dt.rotate(-45)
    dt.shutdown()
    return time.time() - start_time

def test_main():
    test_map()