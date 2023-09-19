from typing import List, Tuple, Union, Iterable, Any
from abc import ABC, abstractmethod

class BaseHardware(ABC):

    @abstractmethod
    def shutdown(self) -> None:
        ...

class BaseDriveTrain(BaseHardware, ABC):
    @abstractmethod
    def stop(self) -> None:
        ...

    @abstractmethod
    def forward_for(self, power: int, centimeters: float) -> None:
        ...

    @abstractmethod
    def forward(self, power: int) -> None:
        ...

    @abstractmethod
    def backward(self, power: int) -> None:
        ...

    @abstractmethod
    def turn_left(self, power: int) -> None:
        ...

    @abstractmethod
    def turn_right(self, power: int) -> None:
        ...

    @abstractmethod
    def rotate(self, degrees_to: float):
        ...

    @property
    @abstractmethod
    def get_left_rear_speed(self) -> Union[int, float]: # speed in centimeters per second
        ...

    @property
    @abstractmethod
    def get_right_rear_speed(self) -> Union[int, float]: # speed in centimeters per second
        ...

    @property
    @abstractmethod
    def get_avg_speed(self) -> float:
        ...


class BaseSensor(BaseHardware, ABC):

    @abstractmethod
    def get_distance(self) -> float:
        ...
    
    @abstractmethod
    def get_distance_at(self, degrees_to: float) -> tuple[float, float]:
        ...

    @abstractmethod
    def scan(
            self, from_degrees: float, 
            to_degrees: float, 
            num_steps: int, 
            samples_per_step: int = 2
            ) -> list[tuple[float, float]]:
        ...


class BaseCamera(BaseHardware, ABC):
    
    @abstractmethod
    def see(self) -> Any:
        ...

    @abstractmethod
    def is_camera_available(self) -> bool:
        ...
    