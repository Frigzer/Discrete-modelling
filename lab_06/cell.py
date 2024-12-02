import numpy as np


# Klasa komórki
class Cell:
    def __init__(self):
        self.input = [0, 0, 0, 0]  # [góra, prawo, dół, lewo]
        self.output = [0, 0, 0, 0]

    def initialize(self, density=0.1):
        self.input = [1 if np.random.rand() < density else 0 for _ in range(4)]

    def collide(self):
        self.output = self.input.copy()
        # Kolizja góra-dół
        if self.input[0] == 1 and self.input[2] == 1 and self.input[1] == 0 and self.input[3] == 0:
            self.output[0], self.output[2] = 0, 0
            self.output[1], self.output[3] = 1, 1
        # Kolizja prawo-lewo
        elif self.input[1] == 1 and self.input[3] == 1 and self.input[0] == 0 and self.input[2] == 0:
            self.output[1], self.output[3] = 0, 0
            self.output[0], self.output[2] = 1, 1
        else:
            self.output = self.input.copy()
