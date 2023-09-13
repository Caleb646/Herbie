import cv2
import time
from typing import Iterable, NamedTuple, List
from dataclasses import dataclass
from tflite_support.task import core, processor, vision

@dataclass(frozen=True)
class ObjectResult:
  score: float
  name: str

@dataclass(frozen=True)
class CameraResult:
  status: bool
  object_list: List[ObjectResult]

class Camera:
  def __init__(self, 
              model: str = "./Models/efficientdet_lite4_model.tflite", 
              camera_id: int = 0, 
              width: int = 320, 
              height: int = 320
          ):
    base_options = core.BaseOptions(file_name=model)
    detection_options = processor.DetectionOptions(
      max_results=3, score_threshold=0.3
      )
    options = vision.ObjectDetectorOptions(
      base_options=base_options, detection_options=detection_options
      )
    self.detector = vision.ObjectDetector.create_from_options(options)
    self.cap = cv2.VideoCapture(camera_id)
    self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

  def see(self) -> Iterable[CameraResult]:
    if not self.cap or not self.cap.isOpened():
      print("Failed to setup camera")
      yield CameraResult(False, [])
    while self.cap.isOpened():
      success, image = self.cap.read()
      if not success:
        print("Failed to read from Camera")
        yield CameraResult(False, [])
      image = cv2.flip(image, 1)
      rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
      input_tensor = vision.TensorImage.create_from_array(rgb_image)
      detection_result = self.detector.detect(input_tensor)
      if detection_result:
        object_list = []
        for detection in detection_result.detections:
          for category in detection.categories:
            object_list.append((category.score, category.category_name))
        yield CameraResult(True, object_list)
      yield CameraResult(True, [])

if __name__ == "__main__":
    #camera_lite3 = Camera(model="./Models/model.tflite", width=320, height=320)
    camera_lite4 = Camera(model="./Models/efficientdet_lite4_model.tflite", width=640, height=640)
    for result in camera_lite4.see():
      print(result)
      time.sleep(1)
