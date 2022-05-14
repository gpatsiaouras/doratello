import os
import time

import cv2

VIDEOS_FOLDER = "videos"


class Recorder:
    def __init__(self):
        """
        Every new instance of recorder creates a new video file AVI
        """
        save_dir = os.path.join(os.path.dirname(__file__), '..', '..', VIDEOS_FOLDER)
        if not os.path.isdir(save_dir):
            os.mkdir(save_dir)

        datetime = time.strftime("%Y%m%d_%H%M%S", time.localtime())
        filename = datetime + '.avi'
        path_to_save = os.path.join(save_dir, filename)

        self.writer = cv2.VideoWriter(path_to_save,
                                      fourcc=cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'),
                                      fps=30,
                                      frameSize=(960, 720))

    def write(self, frame):
        """Write a single frame to the open file"""
        self.writer.write(frame)
