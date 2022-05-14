import os
import time

from playsound import playsound

SOUNDS_FOLDER = "sounds"
SOUND_PLAYING_INTERVAL = 10


class SoundPlayer:
    def __init__(self):
        self.last_played_low_bat = None

    def play(self, sound_file):
        sounds_dir = os.path.join(os.path.dirname(__file__), '..', SOUNDS_FOLDER)
        if not os.path.isdir(sounds_dir):
            print('Sounds directory was not found')
            return

        playsound(os.path.join(sounds_dir, sound_file))

    def play_low_bat(self):
        if not self.last_played_low_bat or time.time() > self.last_played_low_bat + SOUND_PLAYING_INTERVAL:
            self.play("lowbat.wav")
            self.last_played_low_bat = time.time()
