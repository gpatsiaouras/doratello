import cv2

from detectors import FeatureCascadeDetector
from sdk import Tello
from tools import Joystick, PDController, Recorder, add_navigation_info_to_frame

# Constants
VIDEO_WIDTH = 960
VIDEO_HEIGHT = 720


class Main:
    def __init__(self):
        self.tello = Tello()
        self.tello.streamon()

        # Joystick
        self.joy = Joystick(self.tello)

        # PD Controllers
        self.yaw_pd = PDController(VIDEO_WIDTH // 2)
        self.throttle_pd = PDController(VIDEO_HEIGHT // 2)
        self.pitch_pd = PDController(VIDEO_WIDTH // 5)

    def manual_control(self):
        recorder = Recorder()
        try:
            while True:
                self.joy.read()
                if self.tello.is_streaming and self.tello.last_video_frame is not None:
                    recorder.write(self.tello.last_video_frame)
                    cv2.imshow('Tello manual control', self.tello.last_video_frame)
                    k = cv2.waitKey(1) & 0xFF
                    if k == 27:
                        break
                self.joy.clock.tick(30)

            cv2.destroyAllWindows()
        except KeyboardInterrupt:
            self.tello.emergency()

    def follow_face(self):
        face_recognizer = FeatureCascadeDetector()
        recorder = Recorder()
        try:
            while True:
                self.joy.read()
                if self.tello.is_streaming and self.tello.last_video_frame is not None:
                    frame = cv2.resize(self.tello.last_video_frame, (VIDEO_WIDTH, VIDEO_HEIGHT))
                    frame, face = face_recognizer.recognize(frame)

                    if self.tello.is_flying:
                        self.track_face(face)

                    if self.tello.autonomous_flight:
                        self.tello.rc_control(
                            self.tello.values['roll'],
                            self.tello.values['pitch'],
                            self.tello.values['throttle'],
                            self.tello.values['yaw']
                        )

                    frame = add_navigation_info_to_frame({
                        'flying': self.tello.is_flying,
                        'yaw_reaction': self.yaw_pd.pid_reactions[-1] if len(self.yaw_pd.pid_reactions) > 0 else 0,
                        'throttle_reaction': self.throttle_pd.pid_reactions[-1] if len(self.throttle_pd.pid_reactions) > 0 else 0,
                        'pitch_reaction': self.pitch_pd.pid_reactions[-1] if len(self.pitch_pd.pid_reactions) > 0 else 0,
                        'autonomous_flight': self.tello.autonomous_flight
                    }, frame)

                    recorder.write(frame)
                    cv2.imshow('Face recognizer', frame)
                    k = cv2.waitKey(1) & 0xFF
                    if k == 27:
                        break
                self.joy.clock.tick(30)
            cv2.destroyAllWindows()
        except KeyboardInterrupt:
            self.tello.streamoff()
            self.tello.emergency()
            cv2.destroyAllWindows()

    def track_face(self, face):
        if face:
            self.tello.values['yaw'] = self.yaw_pd.run(face.center_x)
            self.tello.values['throttle'] = self.throttle_pd.run(face.center_y) * -1
            self.tello.values['pitch'] = self.pitch_pd.run(face.width) * -1
        else:
            self.tello.reset_velocity_values()
            self.yaw_pd.stop()
            self.throttle_pd.stop()
            self.pitch_pd.stop()


if __name__ == '__main__':
    main = Main()
    # main.follow_face()
    main.manual_control()
