from controllers.xbox_one import BUTTONS, AXES

import pygame


class Joystick:
    def __init__(self, tello):
        # Init pygame
        pygame.init()
        self.clock = pygame.time.Clock()
        pygame.joystick.init()
        self.joy = pygame.joystick.Joystick(0)
        self.joy.init()
        self.tello = tello

        # Physical controller
        self.joy_previous_values = {
            'A': 0,
            'B': 0,
            'C': 0,
            'D': 0,
            'E': 0,
            'G': 0,
            'H': 0,
            'I': 0,
            'LX': 0,
            'LY': 0,
            'RX': 0,
            'RY': 0
        }
        self.values = {}

    def button_pressed(self, button):
        return self.values[button] != self.joy_previous_values[button] and self.values[button]

    def read(self):
        pygame.event.pump()
        self.values = {
            'A': self.joy.get_button(BUTTONS['A']),
            'B': self.joy.get_button(BUTTONS['B']),
            'C': self.joy.get_button(BUTTONS['C']),
            'D': self.joy.get_button(BUTTONS['D']),
            'E': self.joy.get_button(BUTTONS['E']),
            'G': self.joy.get_button(BUTTONS['G']),
            'H': self.joy.get_button(BUTTONS['H']),
            'I': self.joy.get_button(BUTTONS['I']),
            'LX': int(self.joy.get_axis(AXES['LX']) * 100),
            'LY': int(self.joy.get_axis(AXES['LY']) * -1 * 100),
            'RX': int(self.joy.get_axis(AXES['RX']) * 100),
            'RY': int(self.joy.get_axis(AXES['RY']) * -1 * 100)
        }

        if self.button_pressed('A'):
            if self.tello.is_flying:
                self.tello.land()
            else:
                self.tello.takeoff()
        elif self.button_pressed('B'):
            print('Took picture')
            self.tello.take_picture()
        elif self.button_pressed('B'):
            self.tello.set_speed(100)
        elif self.button_pressed('G'):
            print('Emergency')
            self.tello.emergency()
        elif self.button_pressed('H'):
            print('Arm motors')
            self.tello.arm()
        elif self.button_pressed('I'):
            self.tello.autonomous_flight = not self.tello.autonomous_flight
            print('Autonomous flight: ' + str(self.tello.autonomous_flight))
        elif self.button_pressed('C'):
            print('Half speed')
            self.tello.set_speed(50)
        elif self.button_pressed('D'):
            print('Full speed')
            self.tello.set_speed(100)

        if not self.tello.autonomous_flight and self.tello.is_flying:
            self.tello.rc_control(self.values['RX'], self.values['RY'], self.values['LY'], self.values['LX'])
        self.joy_previous_values = self.values
