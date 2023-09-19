from Herbie.CMath.Math import Math, Position
from Tests.utils import *


def test_turning_angle():

    current_and_new = [
        [Position(5, 5, LOOKING_FULL_RIGHT), Position(6, 5), 0],
        [Position(5, 5, LOOKING_FULL_RIGHT), Position(5, 6), TURN_FULL_RIGHT],
        [Position(5, 5, LOOKING_FULL_RIGHT), Position(5, 4), TURN_FULL_LEFT],
        [Position(5, 5, LOOKING_FULL_RIGHT), Position(4, 5), 180],

        [Position(5, 5, LOOKING_FULL_UP), Position(5, 6), 180],
        [Position(5, 5, LOOKING_FULL_UP), Position(5, 4), 0],
        [Position(5, 5, LOOKING_FULL_UP), Position(6, 5), TURN_FULL_RIGHT],
        [Position(5, 5, LOOKING_FULL_UP), Position(4, 5), TURN_FULL_LEFT],

        [Position(5, 5, LOOKING_FULL_LEFT), Position(5, 6), TURN_FULL_LEFT],
        [Position(5, 5, LOOKING_FULL_LEFT), Position(5, 4), TURN_FULL_RIGHT],
        [Position(5, 5, LOOKING_FULL_LEFT), Position(4, 5), 0],
        [Position(5, 5, LOOKING_FULL_LEFT), Position(6, 5), 180],

        [Position(5, 5, LOOKING_FULL_DOWN), Position(6, 5), TURN_FULL_LEFT],
        [Position(5, 5, LOOKING_FULL_DOWN), Position(4, 5), TURN_FULL_RIGHT],
        [Position(5, 5, LOOKING_FULL_DOWN), Position(5, 6), 0],
        [Position(5, 5, LOOKING_FULL_DOWN), Position(5, 4), 180],
        #Position 45 degree turns
        [Position(5, 5, LOOKING_FULL_RIGHT), Position(6, 6), TURN_HALF_RIGHT],
        [Position(5, 5, LOOKING_FULL_RIGHT), Position(4, 4), TURN_ONE_ONEHALF_LEFT],
        [Position(5, 5, LOOKING_FULL_RIGHT), Position(4, 6), TURN_ONO_ONEHALF_RIGHT],
        [Position(5, 5, LOOKING_FULL_RIGHT), Position(6, 4), TURN_HALF_LEFT],
    ]

    for current_pos, target_xy, expected_new_heading in current_and_new:
        new_heading = Math.calc_turning_angle(current_pos, target_xy, should_round=True)
        assert expected_new_heading == new_heading, f"Current: {current_pos} Target: {target_xy} New: {new_heading} != Expected {expected_new_heading}"


def test_calc_new_heading():
    current_new = [
        # current, turn angle, expected heading after turning
        (LOOKING_FULL_RIGHT, TURN_FULL_RIGHT, LOOKING_FULL_DOWN),
        (LOOKING_FULL_RIGHT, TURN_FULL_LEFT, LOOKING_FULL_UP),

        (LOOKING_FULL_UP, TURN_FULL_RIGHT, LOOKING_FULL_RIGHT),
        (LOOKING_FULL_UP, TURN_FULL_LEFT, LOOKING_FULL_LEFT),

        (LOOKING_FULL_LEFT, TURN_FULL_RIGHT, LOOKING_FULL_UP),
        (LOOKING_FULL_LEFT, TURN_FULL_LEFT, LOOKING_FULL_DOWN),

        (LOOKING_FULL_DOWN, TURN_FULL_RIGHT, LOOKING_FULL_LEFT),
        (LOOKING_FULL_DOWN, TURN_FULL_LEFT, LOOKING_FULL_RIGHT),

        (LOOKING_FULL_DOWN, TURN_HALF_LEFT, LOOKING_HALF_DOWN_HALF_LEFT),
        (LOOKING_FULL_DOWN, TURN_HALF_RIGHT, LOOKING_HALF_DOWN_HALF_RIGHT)
    ]
    for current, turn_angle, expected in current_new:
        new_heading = Math.calc_new_heading(current, turn_angle)
        assert expected == new_heading, f"Expected: {expected} != New: {new_heading} Current: {current} Turn Angle: {turn_angle}"