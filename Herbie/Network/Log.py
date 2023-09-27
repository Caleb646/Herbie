import os
from typing import Any, Tuple, Union, List, Iterable
from dataclasses import dataclass
import cv2
import numpy as np
import numpy.typing as npt
import time

def get_local_time() -> str:
    return time.strftime('%b_%A_%I_%M_%S', time.localtime())

@dataclass
class State:
    State_ID_Type = str
    State_Values_Type = Union[str, int, float, Tuple[int, int], List[Tuple[int, int, float]]]
    State_Type = Tuple[ Tuple[State_ID_Type, State_Values_Type], ... ]
    current_step: int = 0
    state_sub_dir: str = get_local_time()
    def save_current_state(
            self,
            mapp: npt.NDArray[np.uint8],
            state: State_Type, 
            main_dir: str,
            filename = f"State_{get_local_time()}",
            new_img_width = 1_000,
            new_img_height = 1_000
            ) -> bool:
        
        main_sub_dir = os.path.join(main_dir, self.state_sub_dir)
        filepath_without_ext = os.path.join(main_sub_dir, f"{filename}_{self.current_step}")
        if not os.path.isdir(main_sub_dir):
            os.mkdir(main_sub_dir)
        resized = cv2.resize( # type: ignore
            mapp, (new_img_width, new_img_height), interpolation = cv2.INTER_NEAREST # type: ignore
            )
        log_file_path =f"{filepath_without_ext}.txt"
        map_path = f"{filepath_without_ext}.jpeg"
        with open(log_file_path, "w") as f:
            lines: List[str] = [f"current_time -> {get_local_time()}"]
            for name, item in state:
                lines.append(f"\n{name} -> {str(item)}")
            f.writelines(lines)
        self.current_step += 1
        return cv2.imwrite(map_path, resized) # type: ignore
    
    def reset(self) -> None:
        self.current_step = 0
        self.state_sub_dir = get_local_time()

def write_to_map(
        mapp: npt.NDArray[np.uint8], 
        objects: list[tuple[int, int]], 
        value: tuple[np.uint8, np.uint8, np.uint8]
        ) -> bool:
    map_changed = False
    for obj in objects:
        if len(obj) == 2:
            x, y = obj
            mapp[y, x] = value
            map_changed = True   
    return map_changed