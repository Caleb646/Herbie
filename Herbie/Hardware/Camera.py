import cv2
import time
from typing import Any, Iterable, NamedTuple, List, Union
from dataclasses import dataclass

import numpy as np

from Herbie.Hardware.Base import BaseCamera

class Camera(BaseCamera):
	def __init__(self, 
				camera_id: int = 0, 
				width: int = 320, 
				height: int = 320
			):
		self.width_ = width
		self.height_ = height
		self.cap = cv2.VideoCapture(camera_id) # type: ignore
		self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width) # type: ignore
		self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height) # type: ignore

	def is_camera_available(self) -> bool:
		return self.cap is not None and self.cap.isOpened()

	def see(self) -> Any:
		status, image = self.cap.read()
		if status == False:
			return status, np.zeros((self.width_, self.height_, 3))
		return status, cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

	def shutdown(self) -> None:
		pass
