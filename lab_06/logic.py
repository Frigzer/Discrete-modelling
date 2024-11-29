# logic.py
import numpy as np

from LGA_Cell import Cell

def streaming(grid, wall):
    height, width = len(grid), len(grid[0])
    new_grid = [[Cell() for _ in range(width)] for _ in range(height)]

    for i in range(height):
        for j in range(width):
            cell = grid[i][j]

            # Obsługa ścian
            if wall[i][j] == -1:
                continue  # Ściana - nie przenosimy cząstek

            # Góra
            if i > 0 and wall[i - 1][j] != -1:
                new_grid[i - 1][j].input[0] = cell.output[0]
            else:  # Odbicie od górnej ściany
                new_grid[i][j].input[2] = cell.output[0]

            # Dół
            if i < height - 1 and wall[i + 1][j] != -1:
                new_grid[i + 1][j].input[2] = cell.output[2]
            else:  # Odbicie od dolnej ściany
                new_grid[i][j].input[0] = cell.output[2]

            # Lewo
            if j > 0 and wall[i][j - 1] != -1:
                new_grid[i][j - 1].input[3] = cell.output[3]
            else:  # Odbicie od lewej ściany
                new_grid[i][j].input[1] = cell.output[3]

            # Prawo
            if j < width - 1 and wall[i][j + 1] != -1:
                new_grid[i][j + 1].input[1] = cell.output[1]
            else:  # Odbicie od prawej ściany
                new_grid[i][j].input[3] = cell.output[1]

    return new_grid


# Funkcja do tworzenia ściany z dziurą
def create_wall_with_hole(height, width, hole_positions):
    """
    Tworzy maskę ściany z dziurą.
    """
    wall = np.zeros((height, width), dtype=int)
    quarter_x = width // 4

    # Tworzenie pionowej ściany
    wall[:, quarter_x] = -1

    # Tworzenie dziury w ścianie
    for hole in hole_positions:
        wall[hole, quarter_x] = 0

    return wall