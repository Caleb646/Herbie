from typing import List, Tuple, Union, Iterable, Any
from abc import ABC, abstractmethod
import time

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


class AbstractSensor(BaseHardware, ABC):

    @abstractmethod
    def get_distance(self) -> float:
        ...

    @abstractmethod
    def get_distance_at(self, angle) -> Tuple[float, float]:
        ...

    @abstractmethod
    def scan(
        self, from_degrees: float, to_degrees: float, num_steps: int, samples_per_step: int
        ) -> List[Tuple[float, float]]:
        ...

    @abstractmethod
    def move_sensor_to(self, angle: float) -> bool:
        ...

class BaseSensor(AbstractSensor):
    
    def get_distance_at(self, degrees_to: float) -> Tuple[float, float]:
        self.move_sensor_to(degrees_to)
        return (degrees_to, self.get_distance())

    def scan(
            self, from_degrees: float, 
            to_degrees: float, 
            num_steps: int, 
            samples_per_step: int = 2
            ) -> List[Tuple[float, float]]:
        half_steps = num_steps // 2 
        #        
        step_size = from_degrees // half_steps
        from_angles = [from_degrees - (i * step_size) for i in range(half_steps)]
        #
        step_size = to_degrees // half_steps
        to_angles = [to_degrees - (i * step_size) for i in range(half_steps)]
        #
        all_angles = sorted(from_angles + to_angles + [0])
        measurements = []
        for angle in all_angles:
            angle_center, distance_center = self.get_distance_at(angle)
            samples = [distance_center]
            sample_size = 20 // samples_per_step
            for i in range(1, (samples_per_step // 2) + 1):
                _, d = self.get_distance_at(angle - sample_size * i)
                samples.append(d)
            for i in range(1, (samples_per_step // 2) + 1):
                _, d = self.get_distance_at(angle + sample_size * i)
                samples.append(d)
            if samples.count(-1) > len(samples) // 2:
                continue
            else:
                filtered_samples = list(filter(lambda dist : dist != -1, samples))
                measurements.append([angle_center, sum(filtered_samples) / len(filtered_samples)])
        return measurements


class BaseCamera(BaseHardware, ABC):
    
    @abstractmethod
    def see(self) -> Any:
        ...

    @abstractmethod
    def is_camera_available(self) -> bool:
        ...
    