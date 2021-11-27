from abc import ABC, abstractmethod
from operator import attrgetter

import cv2

from .Face import Face


class FaceDetector(ABC):
    def __init__(self):
        self.faces = []
        self.detector = None

    @abstractmethod
    def detect(self, frame):
        raise NotImplementedError('Detector should implement this function')

    def recognize(self, frame):
        # Detect the faces
        faces = self.detect(frame)
        # Detect new faces
        self.reset()

        # Draw the rectangle around each face
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
            self.faces.append(Face(x, y, w, h))

        # Find the bigger face
        face_to_track = self.get_bigger_face()
        if face_to_track:
            # Draw a circle at the center
            (h, w) = frame.shape[:2]
            frame_center = (w//2, h//2)
            cv2.circle(frame, (w//2, h//2), 7, (255, 0, 0), -1)
            # Draw a line from the face's center to the center of the frame
            cv2.line(frame, (face_to_track.center_x, face_to_track.center_y), frame_center, (255, 0, 0), 10)

        return frame, face_to_track

    def reset(self):
        self.faces = []

    def get_bigger_face(self):
        if len(self.faces) > 0:
            return max(self.faces, key=attrgetter('area'))
        else:
            return None
