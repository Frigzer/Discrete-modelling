import numpy as np

from LGA_Cell import Cell
from logic import streaming, create_wall_with_hole


# Klasa LGA
class LGA:
    def __init__(self, height, width, density=0.1):
        self.height = height
        self.width = width
        self.grid = [[Cell() for _ in range(width)] for _ in range(height)]

        # Inicjalizacja gazu po lewej stronie ściany
        for i in range(height):
            for j in range(width // 4):
                self.grid[i][j].initialize(density)

        # Tworzenie ściany z dziurą
        self.wall = create_wall_with_hole(height, width, [height // 2 - 1, height // 2, height // 2 + 1])

    def step(self):
        for row in self.grid:
            for cell in row:
                cell.collide()

        self.grid = streaming(self.grid, self.wall)

    def get_state(self):
        state = np.array([[sum(cell.input) for cell in row] for row in self.grid])
        return state