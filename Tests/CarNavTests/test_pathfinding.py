from Herbie.CarNav.Pathfinder import Pathfinder
from Herbie.CarNav.Mapp import Mapp
from Herbie.CMath.Api import Math, Position
from Tests.utils import *

def test_pathfinding():
    mapp = Mapp(11, 11, 10)
    pathfinder = Pathfinder()
    obstacles = [(1, 1), (6, 5), (7, 5)]
    mapp.add_obstacles_xy(obstacles)
    current_position = Position(mapp.num_columns // 2, mapp.num_rows // 2, 0)
    target_position = Position(current_position.x + 5, current_position.y)
    path = pathfinder.a_star(mapp, current_position, target_position)
    expected_path = [
        Position(5, 5), Position(6, 6), Position(7, 6), Position(8, 6), Position(9, 6), Position(10, 5)
        ]
    assert path == expected_path, f"Path: {path} != Expected Path: {expected_path}"
    print("All predicted paths matched their corresponding expected paths")