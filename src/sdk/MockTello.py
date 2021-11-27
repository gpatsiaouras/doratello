import threading
from datetime import datetime

import cv2

from tools import add_stats_to_frame
from tools.stats import Stats


class MockTello:
    def __init__(self):
        self.log = []

        self.command_to_be_received = None

        self.receive_thread = threading.Thread(target=self._receive_thread)
        self.receive_thread.daemon = True
        self.receive_thread.start()

        # Stats
        self.stats = Stats()  # Object to parse and serve stats

        # State
        self.is_streaming = False
        self.is_flying = True
        self.should_take_picture = False
        self.autonomous_flight = False

        # Velocity values
        self.values = {
            'yaw': 0,
            'throttle': 0,
            'pitch': 0,
            'roll': 0
        }

        # RC Control
        self.last_rc_command_sent = datetime.now()
        self.RC_COMMAND_INTERVAL_SEC = 0.2

        # Video
        self.video_thread = None
        self.last_video_frame = None

    def reset_velocity_values(self):
        self.values = {
            'yaw': 0,
            'throttle': 0,
            'pitch': 0,
            'roll': 0
        }

    def send_command(self, command: str, response: str = None):
        print('Send command: {}'.format(command))
        self.command_to_be_received = response

    def _receive_thread(self):
        while True:
            if self.command_to_be_received:
                print('Response: {}'.format(self.command_to_be_received))
                self.command_to_be_received = None

    def get_log(self):
        return self.log

    def take_picture(self):
        self.should_take_picture = True

    def command(self):
        self.send_command('command', 'ok')

    def takeoff(self):
        self.is_flying = True
        self.send_command('takeoff', 'ok')

    def arm(self):
        self.send_command('arm', 'ok')

    def land(self):
        self.is_flying = False
        self.send_command('land', 'ok')

    @staticmethod
    def get_video_capture():
        return cv2.VideoCapture(0)

    def _video_handler(self):
        cap = self.get_video_capture()

        while self.is_streaming:
            ret, frame = cap.read()

            frame = cv2.resize(frame, (1024, 720))

            # Add stats to the frame
            frame = add_stats_to_frame(self.stats, frame)

            # Save frame
            self.last_video_frame = frame

        cap.release()

    def save_frame(self, frame):
        png_name = datetime.now().strftime('%Y%m%d_%H%M%S') + '.png'
        cv2.imwrite(png_name, frame)
        self.should_take_picture = False

    def streamon(self):
        self.send_command('streamon', 'ok')
        self.video_thread = threading.Thread(target=self._video_handler)
        self.video_thread.daemon = True
        self.video_thread.start()
        self.is_streaming = True

    def streamoff(self):
        self.send_command('streamoff', 'ok')
        self.is_streaming = False

    def emergency(self):
        self.send_command('emergency', 'ok')

    def up(self, x: int):
        """Allowed values (20-500)"""
        self.send_command('up {}'.format(x))

    def down(self, x: int):
        """Allowed values (20-500)"""
        self.send_command('down {}'.format(x))

    def left(self, x: int):
        """Allowed values (20-500)"""
        self.send_command('left {}'.format(x))

    def right(self, x: int):
        """Allowed values (20-500)"""
        self.send_command('right {}'.format(x))

    def forward(self, x: int):
        """Allowed values (20-500)"""
        self.send_command('forward {}'.format(x))

    def back(self, x: int):
        """Allowed values (20-500)"""
        self.send_command('back {}'.format(x))

    def cw(self, angle: int):
        """Rotate cw angle°（1-360）"""
        self.send_command('cw {}'.format(angle))

    def ccw(self, angle: int):
        """Rotate ccw angle°（1-360）"""
        self.send_command('ccw {}'.format(angle))

    def flip(self, direction: str):
        """Flip using direction left=l，right=r，forward=f，back=b"""
        self.send_command('flip {}'.format(direction))

    def go(self, x: int, y: int, z: int, speed: int):
        self.send_command('go {} {} {} {}'.format(x, y, z, speed))

    def stop(self):
        self.send_command('stop')

    def curve(self, x1: int, y1: int, z1: int, x2: int, y2: int, z2: int, speed: int):
        self.send_command('curve {} {} {} {} {} {} {}'.format(x1, y1, z1, x2, y2, z2, speed))

    def go_mid(self, x: int, y: int, z: int, speed: int, mid: str):
        self.send_command('go {} {} {} {} {}'.format(x, y, z, speed, mid))

    def curve_mid(self, x1: int, y1: int, z1: int, x2: int, y2: int, z2: int, speed: int, mid: str):
        self.send_command('curve {} {} {} {} {} {} {} {}'.format(x1, y1, z1, x2, y2, z2, speed, mid))

    def jump_mid(self, x: int, y: int, z: int, speed: int, yaw: int, mid1: str, mid2: str):
        self.send_command('jump {} {} {} {} {} {} {}'.format(x, y, z, speed, yaw, mid1, mid2))

    def set_speed(self, speed: int):
        """Set speed to “x” cm/s.x = 10-100"""
        self.send_command('speed {}'.format(speed))

    def rc_control(self, a: int, b: int, c: int, d: int):
        """
            Send rc control commands
            a: roll (-100~100)
            b: pitch (-100~100)
            c: throttle (-100~100)
            d: yaw (-100~100)
        """
        self.send_command('rc {} {} {} {}'.format(a, b, c, d))

    def set_wifi(self, ssid: str, passwrd: str):
        """Set wifi"""
        self.send_command('wifi {} {}'.format(ssid, passwrd))

    def mon(self):
        self.send_command('mon')

    def moff(self):
        self.send_command('moff')

    def mdirection(self, mdir: int):
        self.send_command('mdirection {}'.format(mdir))

    def ap2sta(self, ssid: str, passwrd: str):
        """Set tello wifi for access point"""
        self.send_command('ap {} {}'.format(ssid, passwrd))

    def get_speed(self):
        """speed in cm/s，speed(10-100)"""
        self.send_command('speed?', '5')
        return 5

    def get_battery(self):
        self.send_command('battery?', '70')
        return 70

    def get_time(self):
        self.send_command('time?', '10')
        return 10

    def get_wifi(self):
        self.send_command('wifi?', 'My WIFI')
        return 'My WIFI'

    def get_sdk(self):
        self.send_command('src?', 'my src')
        return 'my src'

    def get_sn(self):
        self.send_command('sn?', '123456')
        return 123456

    def get_height(self):
        self.send_command('height?', '10')
        return 10

    def get_temp(self):
        self.send_command('temp?', '40')
        return 40

    def get_attitude(self):
        self.send_command('attitude?', '2')
        return 2

    def get_baro(self):
        self.send_command('baro?', '1234')
        return 1234

    def get_acceleration(self):
        self.send_command('acceleration?', '0.1')
        return 0.1

    def get_tof(self):
        self.send_command('tof?', '0')
        return 0

    def end(self):
        if self.is_flying:
            self.send_command('land', 'ok')
