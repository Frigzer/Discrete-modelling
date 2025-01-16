import numpy as np

from constants import WALL_POSITION


class Wall:
    def __init__(self, height, width, hole_start, hole_end):
        self.height = height
        self.width = width
        self.wall = np.zeros((height, width), dtype=int)
        self.hole_start = hole_start
        self.hole_end = hole_end
        self.create_wall_with_hole()
        #self.create_custom_wall(self.height // 4 + self.height // 8)

    def create_wall_with_hole(self):
        quarter_x = self.wall.shape[1] // WALL_POSITION

        # Tworzenie pionowej ściany
        self.wall[:, quarter_x] = -1

        # Tworzenie dziury w ścianie
        for hole in range(self.hole_start, self.hole_end + 1):
            self.wall[hole, quarter_x] = 0

    def create_custom_wall(self, height_limit):
        x_position = self.wall.shape[1] // WALL_POSITION

        if 0 <= x_position < self.wall.shape[1] and 0 < height_limit <= self.wall.shape[0]:
            self.wall[-height_limit:, x_position] = -1

    def is_wall(self, i, j):
        return self.wall[i, j] == -1

    def is_hole(self, i, j):
        return self.wall[i, j] == 0

    def get_mask(self):
        return self.wall == -1  # Ściana = True, reszta = False