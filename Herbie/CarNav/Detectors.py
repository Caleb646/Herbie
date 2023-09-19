from Herbie.Hardware.Base import BaseCamera
from Herbie.CarNav.Base import BaseDetector, DetectionResult, DetectedObject
from typing import Iterable, NamedTuple, List, Union
from dataclasses import dataclass
import time


class TFDetector(BaseDetector):
    def __init__(self, camera: BaseCamera,  model_path: str = "./Models/lite0_int8_model.tflite"):
        from tflite_support.task import core, processor, vision

        self.camera_ = camera
        base_options = core.BaseOptions(
            file_name=model_path, num_threads=2
        )
        detection_options = processor.DetectionOptions(
            max_results=3, score_threshold=0.3
        )
        options = vision.ObjectDetectorOptions(
            base_options=base_options, detection_options=detection_options
        )
        self.detector_ = vision.ObjectDetector.create_from_options(options)

    def detect(self) -> DetectionResult:
        if not self.camera_.is_camera_available():
            print("Failed to setup camera")
            return DetectionResult(False, [])
        image = self.camera_.see()
        image = cv2.flip(image, 1) # type: ignore
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB) # type: ignore
        input_tensor = vision.TensorImage.create_from_array(rgb_image)
        detection_result = self.detector_.detect(input_tensor)
        object_list = []
        if detection_result:
            for detection in detection_result.detections:
                for category in detection.categories:
                    object_list.append(DetectedObject(category.score, category.category_name))
        return DetectionResult(True, object_list)
    
def test_detection_fps(
    total_test_time: float,
    model_path="./Models/lite0_int8_model.tflite",
    width = 320,
    height = 320
    ):
    from Herbie.Hardware.Camera import Camera
    camera = Camera(width=width, height=height)
    detector = TFDetector(camera, model_path)
    current_elasped = 0.0
    max_steps = 1_000
    steps_taken = 0
    while total_test_time > current_elasped and steps_taken < max_steps:
        start = time.time()
        result = detector.detect()
        steps_taken += 1
        current_elasped += time.time() - start
        if steps_taken >= max_steps:
            print(f"Hit Max Available Steps: {max_steps} with given time: {total_test_time}")
            print(f"Avg FPS: {steps_taken / total_test_time}")

if __name__ == "__main__":
    test_detection_fps(total_test_time=5.0)