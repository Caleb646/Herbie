from abc import abstractmethod, ABC
from typing import Any, Union
from Src.Hardware.Base import BaseDriveTrain
from Src.CMath.api import Math, Position

from typing import Dict, Iterable, Generator

class AbstractController(ABC):

    @abstractmethod
    def drive(self) -> Generator[bool, None, bool]: # Generator[YieldType, SendType, ReturnType]
        ...

    @abstractmethod
    def step(self) -> bool:
        ...

    @abstractmethod
    def shutdown(self) -> None:
        ...
    
    @abstractmethod
    def get_log_data(self) -> Dict[str, Any]:
        ...

    @abstractmethod
    def move_forward_(self, distance: Union[int, float]) -> None:
        ...

    @abstractmethod
    def turn_(self, turning_angle: Union[int, float]) -> None:
        ...

class BaseController(AbstractController):

    def __init__(self, drive_train: BaseDriveTrain):
        self.drive_train_ = drive_train

    # def drive(self) -> None:
    #     assert False, "Not Implemented"

    # def step(self, new_position: Position) -> Position:
    #     assert False, "Not Implemented"

    # def shutdown(self) -> None:
    #     assert False, "Not Implemented"

    def move_forward_(self, distance: Union[int, float], power=50) -> None:
        self.drive_train_.forward_for(power, distance)

    def turn_(self, turning_angle: float) -> None:
        self.drive_train_.rotate(turning_angle)

    def calc_updated_xy_position_(self, old_position: Position, dist_travelled: float) -> Position:
        direction = Math.project_position(
            old_position.clone(0, 0), dist_travelled, flip_y=True
            )
        return old_position.clone(
            old_position.x + direction.x, old_position.y + direction.y
            )

    def calc_updated_heading_(
            self, old_position: Position, turning_angle: float
            ) -> Position:
        
        return old_position.clone(
            angle = Math.calc_new_heading(old_position.angle, turning_angle)
            )