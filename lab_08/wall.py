import numpy as np

from constants import WALL_POSITION


class Wall:
    def __init__(self, height, width, hole_start, hole_end):
        self.wall = np.zeros((height, width), dtype=int)
        self.hole_start = hole_start
        self.hole_end = hole_end
        self.create_wall_with_hole()

    def create_wall_with_hole(self):
        quarter_x = self.wall.shape[1] // WALL_POSITION

        # Tworzenie pionowej ściany
        self.wall[:, quarter_x] = 0

        # Tworzenie dziury w ścianie
        for hole in range(self.hole_start, self.hole_end + 1):
            self.wall[hole, quarter_x] = -1


    def is_wall(self, i, j):
        return self.wall[i, j] == -1

    def is_hole(self, i, j):
        return self.wall[i, j] == 0

    def get_mask(self):
        return self.wall == -1  # Ściana = True, reszta = False