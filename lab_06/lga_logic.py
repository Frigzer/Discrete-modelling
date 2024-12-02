import numpy as np
import multiprocessing as mp


from cell import Cell
from wall import Wall



# Klasa LGA
class LGA:
    def __init__(self, height, width, density=0.1):
        self.height = height
        self.width = width
        self.grid = [[Cell() for _ in range(width)] for _ in range(height)]
        hole_positions = [height // 2 - 3, height // 2 - 2, height // 2 - 1, height // 2, height // 2 + 1, height // 2 + 2, height // 2 + 3]
        self.wall = Wall(self.grid, hole_positions).create_wall_with_hole()

        # Inicjalizacja gazu po lewej stronie ściany
        for i in range(height):
            for j in range(width // 4):
                self.grid[i][j].initialize(density)

    def streaming(self):
        height, width = len(self.grid), len(self.grid[0])
        new_grid = [[Cell() for _ in range(width)] for _ in range(height)]

        for i in range(height):
            for j in range(width):
                cell = self.grid[i][j]

                # Obsługa ścian
                if self.wall[i][j] == -1:
                    continue  # Ściana - nie przenosimy cząstek

                # Góra
                if i > 0 and self.wall[i - 1][j] != -1:
                    new_grid[i - 1][j].input[0] = cell.output[0]
                else:  # Odbicie od górnej ściany
                    new_grid[i][j].input[2] = cell.output[0]

                # Dół
                if i < height - 1 and self.wall[i + 1][j] != -1:
                    new_grid[i + 1][j].input[2] = cell.output[2]
                else:  # Odbicie od dolnej ściany
                    new_grid[i][j].input[0] = cell.output[2]

                # Lewo
                if j > 0 and self.wall[i][j - 1] != -1:
                    new_grid[i][j - 1].input[3] = cell.output[3]
                else:  # Odbicie od lewej ściany
                    new_grid[i][j].input[1] = cell.output[3]

                # Prawo
                if j < width - 1 and self.wall[i][j + 1] != -1:
                    new_grid[i][j + 1].input[1] = cell.output[1]
                else:  # Odbicie od prawej ściany
                    new_grid[i][j].input[3] = cell.output[1]

        return new_grid


    def step(self):
        for row in self.grid:
            for cell in row:
                cell.collide()


        self.grid = self.streaming()



    def get_state(self):
        state = np.array([[sum(cell.input) for cell in row] for row in self.grid])
        return state
