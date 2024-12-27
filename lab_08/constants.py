import numpy as np

# Kolory
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (200, 200, 200)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
LIGHT_BLUE = (8,124,212)

# Rozmiary komórek i okna
WINDOW_WIDTH = 400
WINDOW_HEIGHT = 400

MENU_HEIGHT = 100

CELL_SIZE = 5
CELL_DENSITY = 2.0

WALL_POSITION = 4
HOLE_SIZE = 7

GRID_WIDTH = WINDOW_WIDTH // CELL_SIZE
GRID_HEIGHT = (WINDOW_HEIGHT - MENU_HEIGHT) // CELL_SIZE

# Współczynniki wagowe dla D2Q9
WEIGHTS = np.array([4.0/9.0, 1.0/9.0, 1.0/9.0, 1.0/9.0, 1.0/9.0, 1.0/36.0, 1.0/36.0, 1.0/36.0, 1.0/36.0], dtype=np.float64)

# Wektory prędkości dla D2Q9
VELOCITIES = np.array([
    [0, 0],
    [1, 0],
    [-1, 0],
    [0, 1],
    [0, -1],
    [1, 1],
    [-1, 1],
    [-1, -1],
    [1, -1]
], dtype=np.int64)

OPPOSITE_DIRECTIONS = np.array([0, 2, 1, 4, 3, 7, 8, 5, 6], dtype=np.int64)  # Przeciwny indeks dla każdego kierunku

