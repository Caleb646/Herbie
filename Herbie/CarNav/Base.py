from abc import abstractmethod, ABC
from typing import Any, Union
from Herbie.Hardware.Base import BaseDriveTrain
from dataclasses import dataclass

from typing import Dict, Iterable, Generator, List

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

    def move_forward_(self, distance: Union[int, float], power=50) -> None:
        self.drive_train_.forward_for(power, distance)

    def turn_(self, turning_angle: float) -> None:
        self.drive_train_.rotate(turning_angle)


@dataclass(frozen=True)
class DetectedObject:
	score: float
	name: str

@dataclass(frozen=True)
class DetectionResult:
	status: bool
	object_list: List[DetectedObject]

	def get_object_score(self, name: str) -> float:
		# its possible that the object shows up in the object_list more than once
		return max(
			filter(lambda obj : obj.name == name, self.object_list), 
			key=lambda obj : obj.score, 
			default = DetectedObject(0.0, "invalid_object")
		).score

class BaseDetector(ABC):

    @abstractmethod
    def detect(self) -> DetectionResult:
        ...