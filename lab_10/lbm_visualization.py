import pygame
import numpy as np
from constants import *
from particle import Particle
from pygame import surfarray
from PIL import Image


class LBMVisualizer:
    def __init__(self, lbm, screen, title, x_offset=0):
        self.lbm = lbm
        self.screen = screen
        self.title = title
        self.x_offset = x_offset

        self.particles = []

        # Przyciski
        self.start_button = pygame.Rect(100, GRID_HEIGHT * CELL_SIZE + 20, 70, 30)
        self.stop_button = pygame.Rect(250, GRID_HEIGHT * CELL_SIZE + 20, 70, 30)
        self.constant_button = pygame.Rect(420, GRID_HEIGHT * CELL_SIZE + 20, 120, 30)
        self.custom_button = pygame.Rect(420, GRID_HEIGHT * CELL_SIZE + 60, 120, 30)
        self.bounce_back_button = pygame.Rect(420, GRID_HEIGHT * CELL_SIZE + 140, 120, 30)

        self.faster_button = pygame.Rect(630, GRID_HEIGHT * CELL_SIZE + 35, 30, 30)
        self.slower_button = pygame.Rect(770, GRID_HEIGHT * CELL_SIZE + 35, 30, 30)

        self.save_button = pygame.Rect(100, GRID_HEIGHT * CELL_SIZE + 60, 70, 30)
        self.load_button = pygame.Rect(250, GRID_HEIGHT * CELL_SIZE + 60, 70, 30)

    def draw_button(self, rect, text, default_color, hover_color):
        if rect.collidepoint(pygame.mouse.get_pos()):
            color = hover_color  # Kolor przy najechaniu myszą
        else:
            color = default_color  # Domyślny kolor

        pygame.draw.rect(self.screen, color, rect)
        pygame.draw.rect(self.screen, BLACK, rect, 2)  # Obramowanie
        font = pygame.font.Font(None, 27)
        text_surf = font.render(text, True, WHITE)
        text_rect = text_surf.get_rect(center=rect.center)
        self.screen.blit(text_surf, text_rect)

    def draw_boundary_condition_type(self, boundary_condition):
        font = pygame.font.Font(None, 27)
        # Tworzenie tekstu z aktualną prędkością
        text_surface = font.render(f"Current boundary condition: {boundary_condition}", True, (0, 0, 0))
        # Umieszczenie tekstu na ekranie (np. w prawym górnym rogu)
        self.screen.blit(text_surface, (850, GRID_HEIGHT * CELL_SIZE + 60))

    def draw_speed(self, speed):
        font = pygame.font.Font(None, 27)
        # Tworzenie tekstu z aktualną prędkością
        text_surface = font.render(f"Speed: {speed}", True, (0, 0, 0))
        # Umieszczenie tekstu na ekranie (np. w prawym górnym rogu)
        self.screen.blit(text_surface, (670, GRID_HEIGHT * CELL_SIZE + 41))

    def draw_iteration(self, iteration):
        font = pygame.font.Font(None, 27)
        # Tworzenie tekstu z aktualną prędkością
        text_surface = font.render(f"Iteration: {iteration}", True, (0, 0, 0))
        # Umieszczenie tekstu na ekranie (np. w prawym górnym rogu)
        self.screen.blit(text_surface, (950, GRID_HEIGHT * CELL_SIZE + 30))

    def draw_grid_and_menu_boundary(self):
        # Ustal miejsce, gdzie ma być granica (pozycja y)
        boundary_x = GRID_WIDTH * CELL_SIZE
        boundary_y = GRID_HEIGHT * CELL_SIZE

        # Rysowanie linii na granicy między gridem a menu
        pygame.draw.line(self.screen, GREEN, (self.x_offset, 0),
                         (self.x_offset + WINDOW_WIDTH, 0), 2)
        pygame.draw.line(self.screen, GREEN, (self.x_offset, boundary_y), (self.x_offset + WINDOW_WIDTH, boundary_y), 2)

        pygame.draw.line(self.screen, GREEN, (self.x_offset, 0),
                         (self.x_offset, boundary_y), 2)
        pygame.draw.line(self.screen, GREEN, (self.x_offset + boundary_x, 0),
                         (self.x_offset + boundary_x, boundary_y), 2)

    def draw_grid(self, mode="density"):
        center_x = self.lbm.width // 2
        center_y = self.lbm.height // 2

        if mode == "density":
            data = np.nan_to_num(self.lbm.rho, nan=0.0, posinf=0.0, neginf=0.0)
            rho = self.lbm.get_rho()
            title = "Density"
        elif mode == "ux":
            data = np.nan_to_num(self.lbm.ux, nan=0.0, posinf=0.0, neginf=0.0)
            ux = self.lbm.get_velocity_x()
            title = "Velocity X"
        elif mode == "uy":
            data = np.nan_to_num(self.lbm.uy, nan=0.0, posinf=0.0, neginf=0.0)
            uy = self.lbm.get_velocity_y()
            title = "Velocity Y"

        for i in range(self.lbm.height):
            for j in range(self.lbm.width):
                x = j - center_x
                y = center_y - i  # Ujemne y dla zgodności z układem współrzędnych
                if self.lbm.wall.is_wall(i, j):  # Ściana
                    color = GREEN
                else:
                    value = data[i, j]
                    if mode == "density":
                        intensity = int(255 * (1 - (rho[i, j] - 0.0) / (CELL_DENSITY - 0.0)))
                        #intensity = max(0, min(255, int(255 * (1 - value / CELL_DENSITY))))
                        intensity = max(0, min(255, intensity))
                        color = (intensity, intensity, intensity)
                    elif mode == "ux":
                        max_speed = MAX_SPEED  # Stała maksymalna wartość prędkości poziomej
                        intensity = int(255 * min(abs(ux[i, j]), max_speed) / max_speed)
                        intensity = max(0, min(255, intensity))
                        if value > 0:
                            color = (255, 255 - intensity, 255 - intensity)  # Czerwona gradacja dla dodatnich
                        else:
                            color = (255 - intensity, 255 - intensity, 255)  # Niebieska gradacja dla ujemnych
                    elif mode == "uy":
                        max_speed = MAX_SPEED  # Stała maksymalna wartość prędkości pionowej
                        intensity = int(255 * min(abs(uy[i, j]), max_speed) / max_speed)
                        intensity = max(0, min(255, intensity))
                        if value < 0:
                            color = (255, 255 - intensity, 255 - intensity)  # Czerwona gradacja dla dodatnich
                        else:
                            color = (255 - intensity, 255 - intensity, 255)  # Niebieska gradacja dla ujemnych

                pygame.draw.rect(
                    self.screen, color,
                    (self.x_offset + j * CELL_SIZE, i * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                )
                #pygame.draw.rect(self.screen, WHITE, (self.x_offset + j * CELL_SIZE, i * CELL_SIZE, CELL_SIZE, CELL_SIZE), 1)

        self.draw_grid_and_menu_boundary()

    def draw_streamlines(self, mode="ux", scale=None):
        """Rysuje linie toku dla prędkości ux lub uy z dostosowaniem do rozmiaru gridu.

        Args:
            mode: "ux" lub "uy" - wybór trybu wizualizacji prędkości.
            scale: Współczynnik skalowania długości linii (jeśli None, obliczany automatycznie).
        """
        if mode == "ux":
            velocity_x = self.lbm.get_velocity_x()
            velocity_y = np.zeros_like(velocity_x)  # Poziomy przepływ
        elif mode == "uy":
            velocity_y = self.lbm.get_velocity_y()
            velocity_x = np.zeros_like(velocity_y)  # Pionowy przepływ
        else:
            raise ValueError("Invalid mode. Use 'ux' or 'uy'.")

        # Automatyczne dopasowanie skali, jeśli nie podano
        if scale is None:
            max_velocity = np.max(np.sqrt(velocity_x ** 2 + velocity_y ** 2))
            scale = 500 / max_velocity if max_velocity > 0 else 1  # Dopasowanie skali

        # Ustawienia dostosowane do rozmiaru gridu
        grid_width = self.lbm.width
        grid_height = self.lbm.height
        buffer_x = grid_width // 20  # Bufor od lewej/prawej krawędzi (5% szerokości)
        buffer_y = grid_height // 20  # Bufor od górnej/dolnej krawędzi (5% wysokości)
        step_x = max(1, grid_width // 30)  # Częstość linii w poziomie (co ~3% szerokości)
        step_y = max(1, grid_height // 30)  # Częstość linii w pionie (co ~3% wysokości)

        for i in range(buffer_y, grid_height - buffer_y, step_y):
            for j in range(buffer_x, grid_width - buffer_x, step_x):
                if self.lbm.wall.is_wall(i, j):
                    continue  # Omijamy ściany

                # Punkt początkowy
                x_start = self.x_offset + j * CELL_SIZE
                y_start = i * CELL_SIZE

                # Kierunek linii na podstawie prędkości
                u = velocity_x[i, j]
                v = -velocity_y[i, j]  # Ujemne, aby dopasować do układu współrzędnych Pygame

                # Punkt końcowy (skalowany kierunek)
                x_end = x_start + scale * u * CELL_SIZE
                y_end = y_start + scale * v * CELL_SIZE

                # Rysowanie linii
                pygame.draw.line(
                    self.screen, (0, 0, 0),  # Czarny kolor
                    (x_start, y_start), (x_end, y_end), 1  # Szerokość linii = 1
                )

    def update(self, speed, iteration, boundary_condition, mode, animating):
        self.draw_grid(mode)


        if mode in ["ux", "uy"]:
            self.draw_streamlines(mode=mode, scale=100)

        if animating:
            self.lbm.update_particles()

        if mode in ["ux", "uy"]:
            self.lbm.draw_particles(self.screen, self.x_offset)

        # Rysowanie przycisków
        self.draw_button(self.start_button, "Start", BLUE, LIGHT_BLUE)
        self.draw_button(self.stop_button, "Stop", BLUE, LIGHT_BLUE)

        #self.draw_button(self.bounce_back_button, "bounce-back", BLUE, LIGHT_BLUE)
        self.draw_button(self.constant_button, "constant", BLUE, LIGHT_BLUE)
        self.draw_button(self.custom_button, "custom", BLUE, LIGHT_BLUE)

        self.draw_button(self.faster_button, "+", BLUE, LIGHT_BLUE)
        self.draw_button(self.slower_button, "-", BLUE, LIGHT_BLUE)
        self.draw_speed(speed)  # Wyświetl prędkość
        self.draw_iteration(iteration)  # Wyświetl prędkość

        self.draw_button(self.save_button, "Save", BLUE, LIGHT_BLUE)
        self.draw_button(self.load_button, "Load", BLUE, LIGHT_BLUE)

        self.draw_boundary_condition_type(boundary_condition)
       # pygame.display.flip()

    def save_visualization_as_bmp(self, base_filename="visualization"):
        modes = ["density", "ux", "uy"]
        for mode in modes:
            self.draw_grid(mode)
            # Wyznaczenie obszaru gridu
            if mode in ["ux", "uy"]:
                self.draw_streamlines(mode=mode, scale=100)  # Linie toku
                self.lbm.draw_particles(self.screen, self.x_offset)  # Cząstki

            grid_rect = pygame.Rect(
                self.x_offset + 2,
                2,
                self.lbm.width * CELL_SIZE - 2,
                self.lbm.height * CELL_SIZE - 2
            )
            grid_surface = self.screen.subsurface(grid_rect)  # Wycięcie gridu z ekranu
            grid_array = surfarray.array3d(grid_surface)
            # Konwersja osi do formatu zgodnego z PIL
            grid_array = grid_array.transpose([1, 0, 2])  # Zamiana (x, y, kolor) na (y, x, kolor)
            # Tworzenie obrazu PIL i zapisywanie jako BMP
            img = Image.fromarray(grid_array)
            img.save(f"{base_filename}_{mode}.bmp")
