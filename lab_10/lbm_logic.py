import json

import numpy as np
import pygame
import random
from PIL import Image
from numba import njit
from wall import Wall
from constants import *
from particle import Particle

@njit
def equilibrium(rho, ux, uy, velocities, weights):
    f_eq = np.zeros(9, dtype=np.float64)  # Rozmiar tylko dla 9 kierunków
    for i in range(9):
        cu = velocities[i][0] * ux + velocities[i][1] * uy
        u_sqr = ux ** 2 + uy ** 2
        f_eq[i] = weights[i] * rho * (1 + 3 * cu + 4.5 * cu ** 2 - 1.5 * u_sqr)
    return f_eq


@njit
def collide_optimized(f_in, f_eq, tau):
    return f_in + (f_eq - f_in) / tau

@njit
def stream_optimized(f_out, wall_mask, height, width, velocities, opposite, boundary_condition):
    f_temp = np.zeros_like(f_out)

    for i in range(height):
        for j in range(width):
            if wall_mask[i, j]:
                continue

            for k in range(9):
                ni = i - velocities[k][1]  # Przesunięcie w osi y
                nj = j - velocities[k][0]  # Przesunięcie w osi x
                if 0 <= ni < height and 0 <= nj < width and not wall_mask[ni, nj]:
                    f_temp[ni, nj, k] = f_out[i, j, k]
                else:
                    f_temp[i, j, opposite[k]] = f_out[i, j, k]

    return f_temp

class LBM:
    def __init__(self, height, width, tau=1.0, boundary_condition="bounce-back"):
        self.height = height
        self.width = width
        self.tau = tau
        self.boundary_condition = boundary_condition

        # Trzy zestawy funkcji rozkładu (wejściowe, równowagowe, wyjściowe)
        self.f_in = np.zeros((height, width, 9), dtype=np.float64)
        self.f_eq = np.zeros((height, width, 9), dtype=np.float64)
        self.f_out = np.zeros((height, width, 9), dtype=np.float64)

        # Gęstość i składowe prędkości
        self.rho = np.ones((height, width), dtype=np.float64)
        self.ux = np.zeros((height, width), dtype=np.float64)
        self.uy = np.zeros((height, width), dtype=np.float64)

        # Inicjalizacja prędkości i gęstości
        self.initialize_density(boundary_condition)

        # Ściana i otwór
        hole_start = height // 2 - HOLE_SIZE
        hole_end = height // 2 + HOLE_SIZE
        self.wall = Wall(height, width, hole_start, hole_end)
        self.particles = []  # Lista cząstek
        self.initialize_particles(num_particles=10)

        self.total_mass = np.sum(self.rho)

    def initialize_particles(self, num_particles=5, y_min=2, y_max=None, particles_per_spot=2, mass_range=(1.0, 5.0)):
        if y_max is None:
            y_max = self.height - 2

        self.particles = []
        for i in range(num_particles):
            x = 1  # Start cząstek blisko lewej krawędzi
            y = y_min + i * (y_max - y_min) // num_particles  # Równomierne rozmieszczenie
            for j in range(particles_per_spot):
                self.particles.append(Particle(x, y, mass_range=mass_range))

    def update_particles(self, velocity_scale=100.0):
        for particle in self.particles:
            grid_x = int(particle.x)
            grid_y = int(particle.y)

            # Sprawdź, czy cząstka jest w granicach siatki
            if 0 <= grid_x < self.width and 0 <= grid_y < self.height:
                ux = self.ux[grid_y, grid_x]
                uy = self.uy[grid_y, grid_x]
                particle.update_position(ux, uy, velocity_scale=velocity_scale)

    def draw_particles(self, screen, x_offset=0):
        for particle in self.particles:
            radius = max(3, int(3 * particle.mass))
            # Rysowanie pozycji cząstki
            pygame.draw.circle(
                screen, particle.color,
                (int(x_offset + particle.x * CELL_SIZE), int(particle.y * CELL_SIZE)),
                3
            )
            # Rysowanie ścieżki cząstki
            for i in range(1, len(particle.path)):
                x1, y1 = particle.path[i - 1]
                x2, y2 = particle.path[i]
                pygame.draw.line(
                    screen, particle.color,
                    (int(x_offset + x1 * CELL_SIZE), int(y1 * CELL_SIZE)),
                    (int(x_offset + x2 * CELL_SIZE), int(y2 * CELL_SIZE)),
                    2
                )

    def initialize_density(self, boundary_condition="bounce-back"):
        #for j in range(self.width // WALL_POSITION):
        #    self.rho[:, j] = CELL_DENSITY  # Gęstość płynu po lewej stronie

        if boundary_condition == "constant":
            # Górna granica:
            self.ux[0, :] = 0.02
            self.uy[0, :] = 0.0

            # Dolna granica:
            self.ux[-1, :] = 0.0
            self.uy[-1, :] = 0.0

            # Lewa i prawa granica:
            for i in range(self.height):
                self.ux[self.height - i - 1, 0] = 0.02 * (i / (self.height - 1))  # Lewa granica
                self.ux[self.height - i - 1, -1] = 0.02 * (i / (self.height - 1))  # Prawa granica
                self.uy[self.height - i - 1, 0] = 0.0
                self.uy[self.height - i - 1, -1] = 0.0

        elif boundary_condition == "custom":
            # Lewa granica: liniowa zmiana prędkości
            for i in range(self.height):
                self.ux[self.height - i - 1, 0] = 0.02 * (i / (self.height - 1))  # Liniowo od 0 do 0.02
                self.uy[self.height - i - 1, 0] = 0.0

            # Prawa granica: stała gęstość
            for i in range(self.height):
                self.rho[i, -1] = 1.0  # Stała gęstość
                self.ux[i, -1] = (self.f_in[i, -1, 0] + self.f_in[i, -1, 3] + self.f_in[i, -1, 4] + 2 * (
                           self.f_in[i, -1, 1] + self.f_in[i, -1, 5] + self.f_in[i, -1, 8]))
                self.uy[i, -1] = 0.0


        # Wyliczenie wartości równowagi dla każdej komórki
        for i in range(self.height):
            for j in range(self.width):
                self.f_in[i, j, :] = equilibrium(self.rho[i, j], self.ux[i, j], self.uy[i, j], VELOCITIES, WEIGHTS)

    def collide(self):
        for i in range(self.height):
            for j in range(self.width):
                self.f_eq[i, j, :] = equilibrium(self.rho[i, j], self.ux[i, j], self.uy[i, j], VELOCITIES,
                                                        WEIGHTS)

        self.f_out = collide_optimized(self.f_in, self.f_eq, self.tau)

    def stream(self, boundary_condition):
        wall_mask = self.wall.get_mask()  # Generowanie maski ścian
        self.f_in = stream_optimized(self.f_out, wall_mask, self.height, self.width, VELOCITIES, OPPOSITE_DIRECTIONS, boundary_condition)

        if boundary_condition == "constant":
            # Narzucanie stałych warunków brzegowych
            # Górna i dolna granica
            for j in range(self.width):
                if not wall_mask[0, j]:
                    # Górna granica
                    self.f_in[0, j, :] = equilibrium(self.rho[0, j], self.ux[0, j], self.uy[0, j], VELOCITIES, WEIGHTS)

                if not wall_mask[-1, j]:
                    # Dolna granica
                    self.f_in[-1, j, :] = equilibrium(self.rho[-1, j], self.ux[-1, j], self.uy[-1, j], VELOCITIES, WEIGHTS)

            for i in range(self.height):
                if not wall_mask[i, 0]:
                    # Lewa granica
                    self.f_in[i, 0, :] = equilibrium(self.rho[i, 0], self.ux[i, 0], self.uy[i, 0], VELOCITIES, WEIGHTS)

                if not wall_mask[i, -1]:
                    # Prawa granica
                    self.f_in[i, -1, :] = equilibrium(self.rho[i, -1], self.ux[i, -1], self.uy[i, -1], VELOCITIES, WEIGHTS)
        elif boundary_condition == "custom":
            # Prawo: warunek otwarty z zadaną gęstością
            for i in range(self.height):
                if not wall_mask[i, -1]:
                    self.rho[i, -1] = 1.0

                    self.ux[i, -1] = 1 - (self.f_in[i, -1, 0] + self.f_in[i, -1, 3] + self.f_in[i, -1, 4] + 2 * (self.f_in[i, -1, 1] + self.f_in[i, -1, 5] + self.f_in[i, -1, 8])) / self.rho[i, -1]
                    self.uy[i, -1] = 0.0

                    self.f_in[i, -1, 1] = self.f_in[i, -1, 2] + 2.0 / 3.0 * self.ux[i, -1] * self.rho[i, -1]
                    self.f_in[i, -1, 5] = self.f_in[i, -1, 7] + 1.0 / 6.0 * self.ux[i, -1] * self.rho[i, -1]
                    self.f_in[i, -1, 8] = self.f_in[i, -1, 6] + 1.0 / 6.0 * self.ux[i, -1] * self.rho[i, -1]

            # Lewo: liniowa zmiana
            for i in range(self.height):
                if not wall_mask[i, 0]:
                    self.f_in[i, 0, :] = equilibrium(self.rho[i, 0], self.ux[i, 0], self.uy[i, 0], VELOCITIES, WEIGHTS)

            # Góra: symetryczny warunek
            for j in range(self.width):
                if not wall_mask[0, j]:
                    self.f_in[0, j, 4] = self.f_in[0, j, 3]
                    self.f_in[0, j, 8] = self.f_in[0, j, 5]
                    self.f_in[0, j, 7] = self.f_in[0, j, 6]

                    self.uy[0, j] = 0.0

            # Dół: bounce-back
            for j in range(self.width):
                if not wall_mask[-1, j]:
                    self.f_in[-1, j, 3] = self.f_in[-1, j, 4]
                    self.f_in[-1, j, 5] = self.f_in[-1, j, 7]
                    self.f_in[-1, j, 6] = self.f_in[-1, j, 8]

    def compute_macroscopic(self):
        self.rho = np.sum(self.f_in, axis=2)
        non_zero_mask = self.rho > 0
        self.ux[non_zero_mask] = np.sum(self.f_in * np.array([v[0] for v in VELOCITIES]), axis=2)[non_zero_mask] / self.rho[non_zero_mask]
        self.uy[non_zero_mask] = np.sum(self.f_in * np.array([v[1] for v in VELOCITIES]), axis=2)[non_zero_mask] / self.rho[non_zero_mask]

        # Ograniczenie prędkości do zakresu [-u_max, u_max]
        u_max = MAX_SPEED
        self.ux = np.clip(self.ux, -u_max, u_max)
        self.uy = np.clip(self.uy, -u_max, u_max)

    def step(self, boundary_condition="bounce-back"):
        total_mass_before = np.sum(self.rho)

        self.compute_macroscopic()
        self.collide()
        self.stream(boundary_condition)

        total_mass_after = np.sum(self.rho)
        if not np.isclose(total_mass_before, total_mass_after, atol=1e-5):
            print(f"Warning: Mass is not conserved! Before: {total_mass_before}, After: {total_mass_after}")

        left_density = np.sum(self.rho[:, :self.width // WALL_POSITION])
        right_density = np.sum(self.rho[:, self.width // WALL_POSITION:])
        print(f"Left density: {left_density}, Right density: {right_density}")

        print(f"At beginning: {self.total_mass}, now: {total_mass_after}")

    def get_rho(self):
        return self.rho

    def get_velocity_x(self):
        return self.ux

    def get_velocity_y(self):
        return self.uy

    def save_simulation_to_json(self, base_filename="simulation", iteration=0):
        simulation_data = {
            "iteration": iteration,
            "rho": self.rho.tolist(),  # Gęstość
            "ux": self.ux.tolist(),  # Prędkość x
            "uy": self.uy.tolist(),  # Prędkość y
            "f_in": self.f_in.tolist(),  # Funkcja dystrybucji f_in
            "f_out": self.f_out.tolist(),  # Opcjonalne f_out
            "boundary_condition": self.boundary_condition,  # Tryb warunków brzegowych

            # Zapis cząstek
            "particles": [
                {
                    "x": p.x, "y": p.y, "mass": p.mass, "color": p.color, "path": p.path
                }
                for p in self.particles
            ],

            # Zapis ściany (jeśli istnieje)
            "wall": {
                "wall_matrix": self.wall.wall.tolist() if self.wall else None,  # Macierz NumPy jako lista
                "hole_start": self.wall.hole_start if self.wall else None,
                "hole_end": self.wall.hole_end if self.wall else None
            } if self.wall else None
        }

        with open(f"{base_filename}_state.json", "w") as f:
            json.dump(simulation_data, f, indent=4)

        print(f"Stan symulacji zapisany do {base_filename}_state.json")

    def load_simulation_from_json(self, base_filename="simulation"):
        with open(f"{base_filename}_state.json", "r") as f:
            simulation_data = json.load(f)

        # Odczytanie podstawowych danych
        self.rho = np.array(simulation_data["rho"])
        self.ux = np.array(simulation_data["ux"])
        self.uy = np.array(simulation_data["uy"])
        self.f_in = np.array(simulation_data["f_in"])  # Pełne odtworzenie f_in
        self.f_out = np.array(simulation_data["f_out"])  # Odtworzenie f_out

        # Odczytanie trybu warunków brzegowych
        self.boundary_condition = simulation_data.get("boundary_condition", "constant")
        print(f"Tryb warunków brzegowych: {self.boundary_condition}")

        # Odczytanie cząstek
        self.particles = [
            Particle(data["x"], data["y"], mass=data["mass"], color=tuple(data["color"]))
            for data in simulation_data["particles"]
        ]
        for p, data in zip(self.particles, simulation_data["particles"]):
            p.path = data["path"]  # Przywrócenie trajektorii

        # Odczytanie ścian (jeśli były zapisane)
        if "wall" in simulation_data and simulation_data["wall"]:
            wall_data = simulation_data["wall"]
            self.wall = Wall(self.height, self.width, wall_data["hole_start"], wall_data["hole_end"])
            self.wall.wall = np.array(wall_data["wall_matrix"])  # Odtworzenie macierzy
            print("Ściany zostały wczytane.")

        iteration = simulation_data.get("iteration", 0)
        print(f"Stan symulacji wczytany z {base_filename}_state.json, Iteracja: {iteration}")

        return iteration, self.boundary_condition
