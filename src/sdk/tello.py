import os
import socket
import threading
import time
from datetime import datetime
from tools import SoundPlayer

import cv2

from tools import Recorder
from tools import Stats
from tools import add_stats_to_frame, add_actions_info_to_frame

STATS_PORT = 8890
COMMANDS_PORT = 8889
PICTURES_FOLDER = "pictures/"
SHOW_MESSAGE_SEC = 2
LOW_BATTERY_WARNING_PERCENT = 20


class Tello:
    def __init__(self, te_ip: str = '192.168.10.1', debug: bool = False, send_command=True):
        self.local_ip = ''
        self.local_port = COMMANDS_PORT
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.local_ip, self.local_port))

        self.stats_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.stats_socket.bind((self.local_ip, STATS_PORT))
        self.stats = Stats()  # Object to parse and serve stats

        self.te_ip = te_ip
        self.te_port = COMMANDS_PORT
        self.te_address = (self.te_ip, self.te_port)
        self.log = []

        self.receive_thread = threading.Thread(target=self._receive_thread)
        self.receive_thread.daemon = True
        self.receive_thread.start()

        self.stats_thread = threading.Thread(target=self._receive_stats_thread)
        self.stats_thread.daemon = True
        self.stats_thread.start()

        # RC Control
        self.last_rc_command_sent = datetime.now()
        self.RC_COMMAND_INTERVAL_SEC = 0.2

        # Video
        self.video_thread = None
        self.last_video_frame = None
        self.recorder = None

        # State
        self.is_streaming = False
        self.is_flying = True
        self.should_take_picture = False
        self.last_picture_taken_at = None
        self.autonomous_flight = False

        # Sounds
        self.sound_player = SoundPlayer()

        # Velocity values
        self.values = {
            'yaw': 0,
            'throttle': 0,
            'pitch': 0,
            'roll': 0
        }

        self.MAX_TIME_OUT = 0.5
        self.debug = debug
        if send_command:
            self.command()

    def reset_velocity_values(self):
        self.values = {
            'yaw': 0,
            'throttle': 0,
            'pitch': 0,
            'roll': 0
        }

    def send_command(self, command: str, query: bool = False):
        if self.debug is True:
            print('Send Command: {}'.format(command))
        self.socket.sendto(command.encode('utf-8'), self.te_address)

        if query:
            start = time.time()
            while not self.log[-1].got_response():
                now = time.time()
                difference = now - start
                if difference > self.MAX_TIME_OUT:
                    print('Connect Time Out!')
                    break

        # if self.debug is True and query is False:
        #     print('Response: {}\n'.format(self.log[-1].get_response()))

    def _receive_stats_thread(self):
        self.stats = Stats()
        while True:
            try:
                received, ip = self.stats_socket.recvfrom(1024)
                self.stats.parse(received)
                if self.stats.get_bat() < LOW_BATTERY_WARNING_PERCENT:
                    self.sound_player.play_low_bat()
            except socket.error as exc:
                print('Error: {}'.format(exc))

    def _receive_thread(self):
        while True:
            try:
                self.response, ip = self.socket.recvfrom(1024)
                self.log.append(self.response.decode('utf-8'))
                if self.debug is True:
                    print('Response: {}\n'.format(self.log[-1]))
            except socket.error as exc:
                print('Error: {}'.format(exc))

    def get_video_capture(self):
        return cv2.VideoCapture('udp://' + self.te_ip + ':11111')

    def _video_handler(self):
        cap = self.get_video_capture()

        while self.is_streaming:
            ret, frame = cap.read()

            if self.should_take_picture:
                self.last_picture_taken_at = time.time()
                self.save_frame(frame)

            # Helps show the message to the user that a picture was taken
            if self.last_picture_taken_at and time.time() > self.last_picture_taken_at + SHOW_MESSAGE_SEC:
                self.last_picture_taken_at = None

            if self.recorder:
                self.recorder.write(frame)

            # Add stats to the frame
            frame = add_stats_to_frame(self.stats, frame)

            # Add other info
            frame = add_actions_info_to_frame({
                "is_recording": True if self.recorder is not None else False,
                "took_picture": True if self.last_picture_taken_at is not None else False,
            }, frame)

            # Save frame
            self.last_video_frame = frame

        cap.release()

    def save_frame(self, frame):
        png_name = datetime.now().strftime('%Y%m%d_%H%M%S') + '.png'
        if not os.path.isdir(PICTURES_FOLDER):
            os.mkdir(PICTURES_FOLDER)
        cv2.imwrite(os.path.join(PICTURES_FOLDER, png_name), frame)
        self.should_take_picture = False

    def get_log(self):
        return self.log

    def take_picture(self):
        self.should_take_picture = True

    def record_video(self):
        """
        If recorder exists it means that we have to stop recording
        else we have to start recording into a new file (new recorder instance)
        :return:
        """
        if not self.recorder:
            self.recorder = Recorder()
        else:
            self.recorder = None

    def command(self):
        self.send_command('command')

    def arm(self):
        self.rc_control(-100, -100, -100, 100)
        time.sleep(0.5)
        self.rc_control(0, 0, 0, 0)
        time.sleep(0.5)
        self.is_flying = True

    def takeoff(self):
        self.is_flying = True
        self.send_command('takeoff')

    def land(self):
        self.is_flying = False
        self.send_command('land')

    def streamon(self):
        self.send_command('streamon')
        self.video_thread = threading.Thread(target=self._video_handler)
        self.video_thread.daemon = True
        self.video_thread.start()
        self.is_streaming = True

    def streamoff(self):
        self.send_command('streamoff')
        self.is_streaming = False

    def emergency(self):
        self.send_command('emergency')
        self.is_flying = False

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
        self.send_command('speed?', True)
        return self.log[-1].get_response()

    def get_battery(self):
        self.send_command('battery?', True)
        return self.log[-1].get_response()

    def get_time(self):
        self.send_command('time?', True)
        return self.log[-1].get_response()

    def get_wifi(self):
        self.send_command('wifi?', True)
        return self.log[-1].get_response()

    def get_sdk(self):
        self.send_command('src?', True)
        return self.log[-1].get_response()

    def get_sn(self):
        self.send_command('sn?', True)
        return self.log[-1].get_response()

    def get_height(self):
        self.send_command('height?', True)
        return self.log[-1].get_response()

    def get_temp(self):
        self.send_command('temp?', True)
        return self.log[-1].get_response()

    def get_attitude(self):
        self.send_command('attitude?', True)
        return self.log[-1].get_response()

    def get_baro(self):
        self.send_command('baro?', True)
        return self.log[-1].get_response()

    def get_acceleration(self):
        self.send_command('acceleration?', True)
        return self.log[-1].get_response()

    def get_tof(self):
        self.send_command('tof?', True)
        return self.log[-1].get_response()

    def end(self):
        if self.is_flying:
            self.land()
