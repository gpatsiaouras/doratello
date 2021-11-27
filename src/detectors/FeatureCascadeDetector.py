import os

import cv2

from .FaceDetector import FaceDetector


class FeatureCascadeDetector(FaceDetector):
    def __init__(self):
        super().__init__()
        # Find the haarcascade_frontalface_default.xml inside the installation of opencv
        cv2_base_dir = os.path.dirname(os.path.abspath(cv2.__file__))
        haar_model = os.path.join(cv2_base_dir, 'data/haarcascade_frontalface_default.xml')

        self.detector = cv2.CascadeClassifier(haar_model)

    def detect(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        return self.detector.detectMultiScale(gray, 1.1, 4)
