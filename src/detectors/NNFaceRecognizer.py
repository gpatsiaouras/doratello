import cv2
from mtcnn.mtcnn import MTCNN

from .FaceDetector import FaceDetector

CONFIDENCE_THRESHOLD = 0.90


class MTCNNDetector(FaceDetector):
    def __init__(self):
        super().__init__()
        self.detector = MTCNN()

    def detect(self, frame):
        boxes = []
        faces = self.detector.detect_faces(frame)
        for face in faces:
            if face['confidence'] > CONFIDENCE_THRESHOLD:
                box = tuple(face['box'])
                boxes.append(box)
                self.add_keypoints_on_frame(face['keypoints'], frame)

        return boxes

    @staticmethod
    def add_keypoints_on_frame(keypoints, frame):
        cv2.circle(frame, (keypoints['left_eye']), 3, (255, 0, 0), 3)
        cv2.circle(frame, (keypoints['right_eye']), 3, (255, 0, 0), 3)
        cv2.circle(frame, (keypoints['nose']), 3, (255, 0, 0), 3)
        cv2.circle(frame, (keypoints['mouth_left']), 3, (255, 0, 0), 3)
        cv2.circle(frame, (keypoints['mouth_right']), 3, (255, 0, 0), 3)
