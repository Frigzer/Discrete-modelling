import numpy as np
from wall import Wall
from constants import *
from numba import njit

@njit
def collide_optimized(f_in, f_eq, tau):
    return f_in + (f_eq - f_in) / tau

@njit
def stream_optimized(f_out, wall_mask, height, width):
    f_temp = np.zeros_like(f_out)

    for i in range(height):
        for j in range(width):
            if wall_mask[i, j]:
                continue

            # Góra
            if i > 0 and not wall_mask[i - 1, j]:
                f_temp[i - 1, j, 0] = f_out[i, j, 0]
            else:
                f_temp[i, j, 2] = f_out[i, j, 0]

            # Dół
            if i < height - 1 and not wall_mask[i + 1, j]:
                f_temp[i + 1, j, 2] = f_out[i, j, 2]
            else:
                f_temp[i, j, 0] = f_out[i, j, 2]

            # Lewo
            if j > 0 and not wall_mask[i, j - 1]:
                f_temp[i, j - 1, 3] = f_out[i, j, 3]
            else:
                f_temp[i, j, 1] = f_out[i, j, 3]

            # Prawo
            if j < width - 1 and not wall_mask[i, j + 1]:
                f_temp[i, j + 1, 1] = f_out[i, j, 1]
            else:
                f_temp[i, j, 3] = f_out[i, j, 1]

    return f_temp

class LBM:
    def __init__(self, height, width, tau=1.0):  # Zwiększony tau dla większej stabilności
        self.height = height
        self.width = width
        self.tau = tau

        # Trzy zestawy funkcji rozkładu (wejściowe, równowagowe, wyjściowe)
        self.f_in = np.zeros((height, width, 4), dtype=np.float32)
        self.f_eq = np.zeros((height, width, 4), dtype=np.float32)
        self.f_out = np.zeros((height, width, 4), dtype=np.float32)

        # Stężenie w każdej komórce
        self.concentration = np.zeros((height, width))

        # Ściana i otwór
        hole_start = height // 2 - HOLE_SIZE
        hole_end = height // 2 + HOLE_SIZE
        self.wall = Wall(height, width, hole_start, hole_end)

        # Inicjalizacja gęstości po lewej stronie ściany
        self.initialize_density()

    def initialize_density(self):
        # Wypełnienie lewej części przestrzeni z równomierną gęstością, aby uniknąć chaosu
        for i in range(self.height):
            for j in range(self.width // WALL_POSITION):
                self.concentration[i, j] = CELL_DENSITY  # Stała gęstość w początkowym obszarze
                self.f_in[i, j, :] = self.concentration[i, j] / 4  # Równowaga początkowa


    def collide(self):
        for i in range(4):
            self.f_eq[:, :, i] = self.concentration / 4  # Funkcja równowagowa

        self.f_out = collide_optimized(self.f_in, self.f_eq, self.tau) # Relaksacja



    def stream(self):
        wall_mask = self.wall.get_mask() # Generowanie maski ścian
        self.f_in = stream_optimized(self.f_out, wall_mask, self.height, self.width)

    def apply_concentration(self):
        # Aktualizacja stężenia na podstawie sumy funkcji rozkładu
        self.concentration = np.sum(self.f_in, axis=2)

    def step(self):
        # Sprawdzenie zachowania masy (debug)
        total_mass_before = np.sum(self.concentration)

        self.collide()
        self.stream()
        self.apply_concentration()

        total_mass_after = np.sum(self.concentration)
        if not np.isclose(total_mass_before, total_mass_after, atol=1e-5):
            print(f"Warning: Mass is not conserved! Before: {total_mass_before}, After: {total_mass_after}")

        # Debug: Sprawdzenie gęstości po lewej i prawej stronie otworu
        left_density = np.sum(self.concentration[:, :self.width // WALL_POSITION])
        right_density = np.sum(self.concentration[:, self.width // WALL_POSITION:])
        print(f"Left density: {left_density}, Right density: {right_density}")

    def get_density(self):
        # Obliczanie gęstości w każdej komórce (to samo co stężenie)
        return self.concentration
