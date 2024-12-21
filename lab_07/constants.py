# Kolory
import numpy as np

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (200, 200, 200)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
LIGHT_BLUE = (8,124,212)

# Rozmiary komórek i okna
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 700

MENU_HEIGHT = 100

CELL_SIZE = 10
CELL_DENSITY = 1.0

WALL_POSITION = 2
HOLE_SIZE = 3

GRID_WIDTH = WINDOW_WIDTH // CELL_SIZE
GRID_HEIGHT = (WINDOW_HEIGHT - MENU_HEIGHT) // CELL_SIZE

VELOCITIES = np.array([
    [1, 0],
    [0, 1],
    [-1, 0],
    [0, -1]
], dtype=np.int32)

OPPOSITE_DIRECTIONS = np.array([2, 3, 0, 1], dtype=np.int32)
