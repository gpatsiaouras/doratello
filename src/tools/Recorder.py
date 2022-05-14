import os
import time

import cv2

VIDEOS_FOLDER = "videos"


class Recorder:
    def __init__(self):
        save_dir = os.path.join(os.path.dirname(__file__), '..', '..', VIDEOS_FOLDER)
        if not os.path.isdir(save_dir):
            os.mkdir(save_dir)

        datetime = time.strftime("%Y%m%d_%H%M", time.localtime())
        filename = datetime + '.avi'
        path_to_save = os.path.join(save_dir, filename)

        self.writer = cv2.VideoWriter(path_to_save, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'), 10, (960, 720))

    def write(self, frame):
        self.writer.write(frame)
