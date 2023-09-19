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
		self.cap = cv2.VideoCapture(camera_id) # type: ignore
		self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width) # type: ignore
		self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height) # type: ignore

	def is_camera_available(self) -> bool:
		return self.cap is not None and self.cap.isOpened()

	def see(self) -> Any:
		status, image = self.cap.read()
		if status == False:
			return status, np.array([])
		return status, image

	def shutdown(self) -> None:
		pass


if __name__ == "__main__":
	#camera_lite3 = Camera(model_path="./Models/model.tflite", width=320, height=320)
	# camera_lite0 = Camera(model_path="./Models/lite0_int8_model.tflite", width=320, height=320)
	#camera_lite4 = Camera(model_path="./Models/efficientdet_lite4_model.tflite", width=640, height=640)
	#camera_gen = camera_lite0.see()
	#print(camera_gen)
	#print(next(camera_gen))
	#print(next(camera_gen))
	# for result in camera_lite0.see():
	#   print(result)
	#   time.sleep(1)
	""""""
