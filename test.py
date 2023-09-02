from typing import Union, Callable
import time

from DriveTrain import DriveTrain
from Mapp import Mapp
from Math import Math
from Pathfinder import Pathfinder

TURN_FULL_LEFT = 90
TURN_FULL_RIGHT = -90

TURN_HALF_LEFT = 45
TURN_HALF_RIGHT = -45

TURN_ONE_ONEHALF_LEFT = 135
TURN_ONO_ONEHALF_RIGHT = -135

LOOKING_UP = 90
LOOKING_DOWN = 270
LOOKING_RIGHT = 0
LOOKING_LEFT = 180

SERVO_LOOK_LEFT = 90 # Servo Look Left
SERVO_LOOK_RIGHT = -90 # Servo Look Right

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


    test_entries = [ 
        ((num_rows // 2, num_colums // 2, 0), (0, 30), (8, 5)), # x, y
        ((num_rows // 2, num_colums // 2, 0), (SERVO_LOOK_LEFT, 30), (5, 2)),
        ((num_rows // 2, num_colums // 2, 0), (SERVO_LOOK_RIGHT, 30), (5, 8)),

        ((num_rows // 2, num_colums // 2, 270), (SERVO_LOOK_RIGHT, 30), (2, 5)),
        ((num_rows // 2, num_colums // 2, 270), (SERVO_LOOK_LEFT, 30), (8, 5)),

        ((num_rows // 2, num_colums // 2, 180), (SERVO_LOOK_LEFT, 30), (5, 8)),
        ((num_rows // 2, num_colums // 2, 180), (SERVO_LOOK_RIGHT, 30), (5, 2)),

        ((num_rows // 2, num_colums // 2, 90), (SERVO_LOOK_LEFT, 30), (2, 5)),
        ((num_rows // 2, num_colums // 2, 90), (SERVO_LOOK_RIGHT, 30), (8, 5)),
    ]
    for entry in test_entries:
        position, measurement, obj_positions = entry
        x, y = obj_positions
        tx, ty = mapp.get_obstacle_idx(position, measurement)
        assert (x, y) == (tx, ty), f"Target: {obj_positions} != Actual: {(tx, ty)} -> Car Pos {position} Servo Angle {measurement}"

def test_turning_angle():

    current_and_new = [
        [(5, 5, LOOKING_RIGHT), (6, 5), 0],
        [(5, 5, LOOKING_RIGHT), (5, 6), TURN_FULL_RIGHT],
        [(5, 5, LOOKING_RIGHT), (5, 4), TURN_FULL_LEFT],
        [(5, 5, LOOKING_RIGHT), (4, 5), 180],

        [(5, 5, LOOKING_UP), (5, 6), 180],
        [(5, 5, LOOKING_UP), (5, 4), 0],
        [(5, 5, LOOKING_UP), (6, 5), TURN_FULL_RIGHT],
        [(5, 5, LOOKING_UP), (4, 5), TURN_FULL_LEFT],

        [(5, 5, LOOKING_LEFT), (5, 6), TURN_FULL_LEFT],
        [(5, 5, LOOKING_LEFT), (5, 4), TURN_FULL_RIGHT],
        [(5, 5, LOOKING_LEFT), (4, 5), 0],
        [(5, 5, LOOKING_LEFT), (6, 5), 180],

        [(5, 5, LOOKING_DOWN), (6, 5), TURN_FULL_LEFT],
        [(5, 5, LOOKING_DOWN), (4, 5), TURN_FULL_RIGHT],
        [(5, 5, LOOKING_DOWN), (5, 6), 0],
        [(5, 5, LOOKING_DOWN), (5, 4), 180],
        
        # 45 degree turns
        [(5, 5, LOOKING_RIGHT), (6, 6), TURN_HALF_RIGHT],
        [(5, 5, LOOKING_RIGHT), (4, 4), TURN_ONE_ONEHALF_LEFT],
        [(5, 5, LOOKING_RIGHT), (4, 6), TURN_ONO_ONEHALF_RIGHT],
        [(5, 5, LOOKING_RIGHT), (6, 4), TURN_HALF_LEFT],
    ]

    for current_pos, target_xy, expected_new_heading in current_and_new:
        new_heading = Math.calc_turning_angle(current_pos, target_xy, should_round=True)
        assert expected_new_heading == new_heading, f"Current: {current_pos} Target: {target_xy} New: {new_heading} != Expected {expected_new_heading}"

def test_calc_new_heading():

    current_new = [
        (LOOKING_RIGHT, TURN_FULL_RIGHT, LOOKING_DOWN),
        (LOOKING_RIGHT, TURN_FULL_LEFT, LOOKING_UP),

        (LOOKING_RIGHT, TURN_FULL_RIGHT, LOOKING_DOWN),
        (LOOKING_RIGHT, TURN_FULL_LEFT, LOOKING_UP),
    ]


def test_pathfinding():
    mapp = Mapp(11, 11, 10)
    pathfinder = Pathfinder()
    obstacles = [(1, 1), (6, 5), (7, 5)]
    mapp.add_obstacles_xy(obstacles)
    current_position = (mapp.num_columns // 2, mapp.num_rows // 2, 0)
    target_position = (current_position[0] + 5, current_position[1])
    path = pathfinder.a_star(mapp, current_position, target_position)
    expected_path = [(5, 5), (6, 6), (7, 6), (8, 6), (9, 5), (10, 5)]
    assert path == expected_path, f"Path: {path} != Expected Path: {expected_path}"

def test_drive_train():
    dt = DriveTrain()
    start_time = time.time()
    dt.rotate(-45)
    dt.shutdown()
    return time.time() - start_time