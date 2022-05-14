import matplotlib.pyplot as plt
import numpy as np


class PDController:
    def __init__(self, value, kp=0.2, kd=0.2, max_reaction=100):
        # Config
        self.kp = kp
        self.kd = kd
        self.value = value
        self.max_reaction = max_reaction
        self.pid_previous_error = 0
        # self.pid_d_previous_error = 0

        # State
        self.running = False

        # Logs
        self.pid_reactions = []

    def stop(self):
        self.running = False
        self.pid_reactions.append(0)
        self.pid_previous_error = 0

    def run(self, target):
        error = target - self.value
        # current_d_error = error - self.pid_previous_error
        # reaction = self.kp * error + self.kd * (0.5 * current_d_error + 0.5 * self.pid_d_previous_error)
        reaction = self.kp * error + self.kd * (error - self.pid_previous_error)
        reaction = int(np.clip(reaction, -self.max_reaction, self.max_reaction))

        self.pid_reactions.append(reaction)
        self.pid_previous_error = error
        # self.pid_d_previous_error = current_d_error

        return reaction

    def plot_reactions(self):
        plt.plot(self.pid_reactions)
        plt.ylabel('Reactions')
        plt.show()
