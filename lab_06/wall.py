import numpy as np


class Wall:
    def __init__(self, grid, hole_positions=None):
        self.grid = grid
        self.height = len(grid)
        self.width = len(grid[0])
        self.hole_positions = hole_positions
        self.create_wall_with_hole()

    # Funkcja do tworzenia ściany z dziurą
    def create_wall_with_hole(self):
        """Tworzy maskę ściany z dziurą."""

        wall = np.zeros((self.height, self.width), dtype=int)
        quarter_x = self.width // 4

        # Tworzenie pionowej ściany
        wall[:, quarter_x] = -1

        # Tworzenie dziury w ścianie
        for hole in self.hole_positions:
            wall[hole, quarter_x] = 0

        return wall
