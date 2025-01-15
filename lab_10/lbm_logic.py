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
        """Inicjalizuje cząstki w siatce."""
        if y_max is None:
            y_max = self.height - 2  # Domyślnie omijamy 2 górne/dolne wiersze

        self.particles = []
        for i in range(num_particles):
            x = 1  # Start cząstek blisko lewej krawędzi
            y = y_min + i * (y_max - y_min) // num_particles  # Równomierne rozmieszczenie
            for j in range(particles_per_spot):
                self.particles.append(Particle(x, y, mass_range=mass_range))

    def update_particles(self, velocity_scale=50.0):
        """Aktualizuje pozycje cząstek na podstawie prędkości siatki."""
        for particle in self.particles:
            grid_x = int(particle.x)
            grid_y = int(particle.y)

            # Sprawdź, czy cząstka jest w granicach siatki
            if 0 <= grid_x < self.width and 0 <= grid_y < self.height:
                ux = self.ux[grid_y, grid_x]
                uy = self.uy[grid_y, grid_x]
                particle.update_position(ux, uy, velocity_scale=velocity_scale)

    def draw_particles(self, screen, x_offset=0):
        """Rysuje cząstki na ekranie."""
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

    def save_simulation_as_bmp(self, base_filename="simulation", iteration=0):
        """Zapisuje stan symulacji (gęstość, ux, uy) jako bitmapy oraz zapisuje particles i iterację."""
        # Zapis gęstości
        density_img = self._invert_visualize_density(self.get_rho())
        density_img.save(f"{base_filename}_density.bmp")

        # Zapis prędkości
        ux_img = self._visualize_velocity(self.get_velocity_x())
        uy_img = self._visualize_velocity(self.get_velocity_y())
        ux_img.save(f"{base_filename}_ux.bmp")
        uy_img.save(f"{base_filename}_uy.bmp")

        # Zapis cząstek i iteracji
        if hasattr(self, "particles") and self.particles:
            particles_data = [{"x": p.x, "y": p.y, "mass": p.mass, "color": p.color, "path": p.path} for p in self.particles]
            simulation_data = {
                "iteration": iteration,
                "particles": particles_data
            }
            with open(f"{base_filename}_particles.json", "w") as f:
                import json
                json.dump(simulation_data, f, indent=4)
            print(f"Particles i iteracja zapisane do pliku {base_filename}_simulation.json")

    def load_simulation_from_bmp(self, base_filename="simulation"):
        """Wczytuje stan symulacji (gęstość, ux, uy) z bitmap oraz cząstki i iterację."""
        # Wczytanie gęstości
        density_img = Image.open(f"{base_filename}_density.bmp").convert('L')
        self.rho = self._invert_denormalize_density(np.array(density_img))

        # Wczytanie prędkości
        ux_img = Image.open(f"{base_filename}_ux.bmp").convert('RGB')
        uy_img = Image.open(f"{base_filename}_uy.bmp").convert('RGB')
        self.ux = self._denormalize_velocity(np.array(ux_img))
        self.uy = self._denormalize_velocity(np.array(uy_img))

        # Wczytanie cząstek i iteracji
        with open(f"{base_filename}_particles.json", "r") as f:
            import json
            simulation_data = json.load(f)
        self.particles = [
            Particle(data["x"], data["y"], mass=data["mass"], color=tuple(data["color"]))
            for data in simulation_data["particles"]
        ]
        for p, data in zip(self.particles, simulation_data["particles"]):
            p.path = data["path"]  # Przywrócenie trajektorii

        # Odczytanie iteracji
        iteration = simulation_data.get("iteration", 0)
        print(f"Particles i iteracja wczytane z pliku {base_filename}_particles.json, Iteracja: {iteration}")

        # Aktualizacja funkcji równowagowych
        for i in range(self.height):
            for j in range(self.width):
                self.f_in[i, j, :] = equilibrium(self.rho[i, j], self.ux[i, j], self.uy[i, j], VELOCITIES, WEIGHTS)

        return iteration  # Zwracamy numer iteracji

    def _invert_visualize_density(self, rho):
        """Zapisuje gęstość do bitmapy z odwroconą skalą: czarny = 1, biały = 0."""
        intensity = 255 * (1 - (rho / CELL_DENSITY))  # Czarny = maksymalna gęstość
        intensity = np.clip(intensity, 0, 255).astype(np.uint8)
        return Image.fromarray(intensity, mode="L")

    def _invert_visualize_velocity(self, velocity):
        """Generuje odwrócony obraz prędkości w skali czerwono-niebieskiej."""
        max_speed = MAX_SPEED
        intensity = 255 * np.minimum(np.abs(velocity), max_speed) / max_speed
        intensity = np.clip(intensity, 0, 255).astype(np.uint8)

        red_channel = np.where(velocity > 0, intensity, 0).astype(np.uint8)
        blue_channel = np.where(velocity < 0, intensity, 0).astype(np.uint8)
        green_channel = np.zeros_like(intensity, dtype=np.uint8)

        # Zamiana kolorów: biały = 0 prędkości
        red_channel = 255 - red_channel
        blue_channel = 255 - blue_channel
        return Image.merge("RGB", (
            Image.fromarray(red_channel, mode="L"),
            Image.fromarray(green_channel, mode="L"),
            Image.fromarray(blue_channel, mode="L")
        ))

    def _invert_denormalize_density(self, density_image):
        """Odczytuje gęstość z bitmapy i odwraca skalę: biały = 0, czarny = 1."""
        return CELL_DENSITY * (1 - density_image / 255)

    def _invert_denormalize_velocity(self, velocity_image):
        """Odwrócona denormalizacja prędkości."""
        red_channel = velocity_image[:, :, 0].astype(np.float64)
        blue_channel = velocity_image[:, :, 2].astype(np.float64)
        normalized = (255 - red_channel - (255 - blue_channel)) / 255  # Odwracanie
        return normalized * MAX_SPEED

    def _visualize_velocity(self, velocity):
        """Generuje obraz prędkości w skali czerwono-niebieskiej."""
        max_speed = MAX_SPEED
        intensity = 255 * np.minimum(np.abs(velocity), max_speed) / max_speed
        intensity = np.clip(intensity, 0, 255).astype(np.uint8)

        red_channel = np.where(velocity > 0, intensity, 0).astype(np.uint8)
        blue_channel = np.where(velocity < 0, intensity, 0).astype(np.uint8)
        green_channel = np.zeros_like(intensity, dtype=np.uint8)

        return Image.merge("RGB", (
            Image.fromarray(red_channel, mode="L"),
            Image.fromarray(green_channel, mode="L"),
            Image.fromarray(blue_channel, mode="L")
        ))

    def _denormalize_velocity(self, velocity_image):
        """Odczytuje prędkości z bitmapy w skali czerwono-niebieskiej."""
        red_channel = velocity_image[:, :, 0].astype(np.float64)
        blue_channel = velocity_image[:, :, 2].astype(np.float64)
        normalized = (red_channel - blue_channel) / 255  # Skala od -1 do 1
        return normalized * MAX_SPEED