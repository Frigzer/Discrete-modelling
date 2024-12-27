import numpy as np
import math

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
        self.rho[:, :] = 0.5#1e-6
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
            self.rho[:, j] = CELL_DENSITY  # Gęstość płynu po lewej stronie

        #self.ux[:, :] = 0.0
        #self.uy[:, :] = 0.0

       # for i in range(9):
       #     cu = VELOCITIES[i][0] * self.ux + VELOCITIES[i][1] * self.uy
       #     u_sqr = self.ux ** 2 + self.uy ** 2
       #     self.f_in[:, :, i] = WEIGHTS[i] * self.rho * (1 + 3 * cu + 4.5 * cu ** 2 - 1.5 * u_sqr)

    def collide(self):
        wall_mask = self.wall.get_mask()
        print("rho == 0 count:", np.sum(self.rho == 0))
        print("rho min/max:", np.min(self.rho), np.max(self.rho))
        print("ux min/max:", np.min(self.ux), np.max(self.ux))
        print("uy min/max:", np.min(self.uy), np.max(self.uy))
        indices = np.where(self.uy == -1.0)
        print("Indices with uy == -1.0:", indices)
        for i in range(9):
            cu = VELOCITIES[i][0] * self.ux + VELOCITIES[i][1] * self.uy
            u_sqr = self.ux ** 2 + self.uy ** 2
            self.f_eq[:, :, i] = WEIGHTS[i] * self.rho * (1 + 3 * cu + 4.5 * cu ** 2 - 1.5 * u_sqr)

        #self.f_eq = np.maximum(self.f_eq, 0)
        #self.ux[wall_mask] = 0
        #self.uy[wall_mask] = 0

        if np.any(self.f_in < 0):
            print("f_in < 0 in collision!!!")
        if np.any(self.f_eq < 0):
            print("f_eq < 0 in collision!!!")

        #self.f_out = self.f_in + (self.f_eq - self.f_in) / self.tau
        self.f_out = collide_optimized(self.f_in, self.f_eq, self.tau)
        if np.any(self.f_out < 0):
            print("f_out < 0 in collision!!!")

    def stream(self):

        wall_mask = self.wall.get_mask() # Generowanie maski ścian
        f_temp = np.zeros_like(self.f_out)
        '''
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
        '''
        self.f_in = stream_optimized(self.f_out, wall_mask, self.height, self.width, VELOCITIES, OPPOSITE_DIRECTIONS)

    def compute_macroscopic(self):
        self.rho = np.sum(self.f_in, axis=2)
        non_zero_mask = self.rho > 0
        self.ux[non_zero_mask] = np.sum(self.f_in * np.array([v[0] for v in VELOCITIES]), axis=2)[non_zero_mask] / self.rho[non_zero_mask]
        self.uy[non_zero_mask] = np.sum(self.f_in * np.array([v[1] for v in VELOCITIES]), axis=2)[non_zero_mask] / self.rho[non_zero_mask]

        # Maksymalna dozwolona wartość prędkości
        u_max = 0.7  # Możesz dostosować tę wartość

        # Ograniczenie prędkości do zakresu [-u_max, u_max]
        self.ux = np.clip(self.ux, -u_max, u_max)
        self.uy = np.clip(self.uy, -u_max, u_max)

    def step(self):
        # Sprawdzenie zachowania masy (debug)
        total_mass_before = np.sum(self.rho)

        self.collide()
        print(f"After collide - Min f_in: {np.min(self.f_in)}, Min f_eq: {np.min(self.f_eq)}")
        self.stream()
        print(f"After stream - Min f_in: {np.min(self.f_in)}")
        self.compute_macroscopic()

        total_mass_after = np.sum(self.rho)
        if not np.isclose(total_mass_before, total_mass_after, atol=1e-5):
            print(f"Warning: Mass is not conserved! Before: {total_mass_before}, After: {total_mass_after}")

        # Debug: Sprawdzenie gęstości po lewej i prawej stronie otworu
        left_density = np.sum(self.rho[:, :self.width // WALL_POSITION])
        right_density = np.sum(self.rho[:, self.width // WALL_POSITION:])
        print(f"Left density: {left_density}, Right density: {right_density}")

    def get_rho(self):
        return self.rho

    def get_velocity_x(self):
        return self.ux

    def get_velocity_y(self):
        return self.uy
