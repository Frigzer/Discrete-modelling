import numpy as np

from wall import Wall
from constants import *
from numba import njit

@njit
def collide_optimized(f_in, f_eq, tau):
    return f_in + (f_eq - f_in) / tau

@njit
def stream_optimized(f_out, wall_mask, height, width, velocities, opposite):
    f_temp = np.zeros_like(f_out)

    for i in range(height):
        for j in range(width):
            if wall_mask[i, j]:
                continue

            for k in range(9):
                ni = i - velocities[k][0]
                nj = j - velocities[k][1]
                if 0 <= ni < height and 0 <= nj < width and not wall_mask[ni, nj]:
                    f_temp[ni, nj, k] = f_out[i, j, k]
                else:
                    f_temp[i, j, opposite[k]] = f_out[i, j, k]
    return f_temp


class LBM:
    def __init__(self, height, width, tau=1.0):  # Zwiększony tau dla większej stabilności
        self.height = height
        self.width = width
        self.tau = tau

        # Trzy zestawy funkcji rozkładu (wejściowe, równowagowe, wyjściowe)
        self.f_in = np.zeros((height, width, 9), dtype=np.float64)
        self.f_eq = np.zeros((height, width, 9), dtype=np.float64)
        self.f_out = np.zeros((height, width, 9), dtype=np.float64)

        # Gęstość i składowe prędkości
        self.rho = np.zeros((height, width), dtype=np.float64)
        self.rho[:, :] = 1e-4
        self.ux = np.zeros((height, width), dtype=np.float64)
        self.uy = np.zeros((height, width), dtype=np.float64)

        # Ściana i otwór
        hole_start = height // 2 - HOLE_SIZE
        hole_end = height // 2 + HOLE_SIZE
        self.wall = Wall(height, width, hole_start, hole_end)

        # Inicjalizacja gęstości po lewej stronie ściany
        self.initialize_density()

    def initialize_density(self):
        # Funkcje rozkładu w równowadze początkowej po lewej stronie
        for j in range(self.width // WALL_POSITION):
            self.rho[:, j] = 1.0  # Gęstość płynu po lewej stronie

        self.ux[:, :] = 0.0
        self.uy[:, :] = 0.0

        for i in range(9):
            cu = VELOCITIES[i][0] * self.ux + VELOCITIES[i][1] * self.uy
            u_sqr = self.ux ** 2 + self.uy ** 2
            self.f_in[:, :, i] = WEIGHTS[i] * self.rho * (1 + 3 * cu + 4.5 * cu ** 2 - 1.5 * u_sqr)

    def collide(self):
        wall_mask = self.wall.get_mask()
        for i in range(9):
            cu = VELOCITIES[i][0] * self.ux + VELOCITIES[i][1] * self.uy
            u_sqr = self.ux ** 2 + self.uy ** 2
            self.f_eq[:, :, i] = WEIGHTS[i] * self.rho * (1 + 3 * cu + 4.5 * cu ** 2 - 1.5 * u_sqr)

        self.f_eq = np.maximum(self.f_eq, 0)
        self.ux[wall_mask] = 0
        self.uy[wall_mask] = 0

        self.f_out = self.f_in + (self.f_eq - self.f_in) / self.tau
        #self.f_out = collide_optimized(self.f_in, self.f_eq, self.tau)

    def stream(self):
        wall_mask = self.wall.get_mask() # Generowanie maski ścian
        f_temp = np.zeros_like(self.f_out)

        for i in range(self.height):
            for j in range(self.width):
                if wall_mask[i, j]:
                    continue

                for k in range(9):
                    ni = i - VELOCITIES[k][0]
                    nj = j - VELOCITIES[k][1]
                    if 0 <= ni < self.height and 0 <= nj < self.width and not wall_mask[ni, nj]:
                        f_temp[ni, nj, k] = self.f_out[i, j, k]
                    else:
                        f_temp[i, j, OPPOSITE_DIRECTIONS[k]] = self.f_out[i, j, k]
        self.f_in = f_temp
        # Aktualizacja prędkości w komórkach przy ścianach
        for i in range(self.height):
            for j in range(self.width):
                if wall_mask[i, j]:
                    # Zerowanie prędkości przy ścianach (no-slip condition)
                    self.ux[i, j] = 0
                    self.uy[i, j] = 0
        #self.f_in = stream_optimized(self.f_out, wall_mask, self.height, self.width, VELOCITIES, OPPOSITE_DIRECTIONS)

    def apply_boundary_conditions(self):
        # Lewa krawędź
        self.f_in[:, 0, 1] = self.f_out[:, 0, 3]  # f1 ↔ f3
        self.f_in[:, 0, 5] = self.f_out[:, 0, 7]  # f5 ↔ f7
        self.f_in[:, 0, 8] = self.f_out[:, 0, 6]  # f8 ↔ f6

        # Prawa krawędź
        self.f_in[:, -1, 3] = self.f_out[:, -1, 1]  # f3 ↔ f1
        self.f_in[:, -1, 7] = self.f_out[:, -1, 5]  # f7 ↔ f5
        self.f_in[:, -1, 6] = self.f_out[:, -1, 8]  # f6 ↔ f8

        # Górna krawędź
        self.f_in[0, :, 2] = self.f_out[0, :, 4]  # f2 ↔ f4
        self.f_in[0, :, 5] = self.f_out[0, :, 7]  # f5 ↔ f7
        self.f_in[0, :, 6] = self.f_out[0, :, 8]  # f6 ↔ f8

        # Dolna krawędź
        self.f_in[-1, :, 4] = self.f_out[-1, :, 2]  # f4 ↔ f2
        self.f_in[-1, :, 7] = self.f_out[-1, :, 5]  # f7 ↔ f5
        self.f_in[-1, :, 8] = self.f_out[-1, :, 6]  # f8 ↔ f6

        # Zerowanie prędkości na krawędziach
        self.ux[:, 0] = 0  # Lewa
        self.ux[:, -1] = 0  # Prawa
        self.uy[0, :] = 0  # Górna
        self.uy[-1, :] = 0  # Dolna

    def apply_macroscopic_variables(self):
        epsilon = 1e-10  # Mała wartość zapobiegająca dzieleniu przez zero
        self.rho = np.sum(self.f_in, axis=2)  # Gęstość
        self.ux = np.sum(self.f_in * np.array([v[0] for v in VELOCITIES]), axis=2) / (self.rho + epsilon)
        self.uy = np.sum(self.f_in * np.array([v[1] for v in VELOCITIES]), axis=2) / (self.rho + epsilon)

    def compute_macroscopic(self):
        self.rho = np.sum(self.f_in, axis=2)
        non_zero_mask = self.rho > 0
        self.ux[non_zero_mask] = np.sum(self.f_in * np.array([v[0] for v in VELOCITIES]), axis=2)[non_zero_mask] / self.rho[non_zero_mask]
        self.uy[non_zero_mask] = np.sum(self.f_in * np.array([v[1] for v in VELOCITIES]), axis=2)[non_zero_mask] / self.rho[non_zero_mask]

    def step(self):
        # Sprawdzenie zachowania masy (debug)
        total_mass_before = np.sum(self.rho)

        self.apply_macroscopic_variables()
        self.collide()
        print(f"After collide - Min f_in: {np.min(self.f_in)}, Min f_eq: {np.min(self.f_eq)}")
        self.stream()
        print(f"After stream - Min f_in: {np.min(self.f_in)}")
        #self.compute_macroscopic()

        total_mass_after = np.sum(self.rho)
        if not np.isclose(total_mass_before, total_mass_after, atol=1e-5):
            print(f"Warning: Mass is not conserved! Before: {total_mass_before}, After: {total_mass_after}")

        # Debug: Sprawdzenie gęstości po lewej i prawej stronie otworu
        left_density = np.sum(self.rho[:, :self.width // WALL_POSITION])
        right_density = np.sum(self.rho[:, self.width // WALL_POSITION:])
        print(f"Left density: {left_density}, Right density: {right_density}")

    def get_velocity(self):
        return self.u
