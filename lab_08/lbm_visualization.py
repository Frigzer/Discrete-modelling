import pygame
import numpy as np
from constants import *

class LBMVisualizer:
    def __init__(self, lbm, screen, title, x_offset=0):
        self.lbm = lbm
        self.screen = screen
        self.title = title
        self.x_offset = x_offset

        # Przyciski
        self.start_button = pygame.Rect(50, GRID_HEIGHT * CELL_SIZE + 20, 100, 50)
        self.stop_button = pygame.Rect(200, GRID_HEIGHT * CELL_SIZE + 20, 100, 50)
        self.reset_button = pygame.Rect(350, GRID_HEIGHT * CELL_SIZE + 20, 100, 50)

        self.faster_button = pygame.Rect(500, GRID_HEIGHT * CELL_SIZE + 20, 50, 50)
        self.slower_button = pygame.Rect(700, GRID_HEIGHT * CELL_SIZE + 20, 50, 50)

    def draw_button(self, rect, text, default_color, hover_color):
        if rect.collidepoint(pygame.mouse.get_pos()):
            color = hover_color  # Kolor przy najechaniu myszą
        else:
            color = default_color  # Domyślny kolor

        pygame.draw.rect(self.screen, color, rect)
        pygame.draw.rect(self.screen, BLACK, rect, 2)  # Obramowanie
        font = pygame.font.Font(None, 36)
        text_surf = font.render(text, True, WHITE)
        text_rect = text_surf.get_rect(center=rect.center)
        self.screen.blit(text_surf, text_rect)

    def draw_speed(self, speed):
        font = pygame.font.Font(None, 36)
        # Tworzenie tekstu z aktualną prędkością
        text_surface = font.render(f"Speed: {speed}", True, (0, 0, 0))
        # Umieszczenie tekstu na ekranie (np. w prawym górnym rogu)
        self.screen.blit(text_surface, (570, GRID_HEIGHT * CELL_SIZE + 35))

    def draw_grid_and_menu_boundary(self):
        # Ustal miejsce, gdzie ma być granica (pozycja y)
        boundary_y = GRID_HEIGHT * CELL_SIZE

        # Rysowanie linii na granicy między gridem a menu
        pygame.draw.line(self.screen, LIGHT_BLUE, (self.x_offset, boundary_y), (self.x_offset + WINDOW_WIDTH, boundary_y), 2)


    def draw_grid(self, mode="density"):
        if mode == "density":
            data = np.nan_to_num(self.lbm.rho, nan=0.0, posinf=0.0, neginf=0.0)
            title = "Density"
        elif mode == "ux":
            data = np.nan_to_num(self.lbm.ux, nan=0.0, posinf=0.0, neginf=0.0)
            title = "Velocity X"
        elif mode == "uy":
            data = np.nan_to_num(self.lbm.uy, nan=0.0, posinf=0.0, neginf=0.0)
            title = "Velocity Y"

        for i in range(self.lbm.height):
            for j in range(self.lbm.width):
                if self.lbm.wall.is_wall(i, j):  # Ściana
                    color = GREEN
                else:
                    value = data[i, j]
                    if mode == "density":
                        intensity = int(255 * (1 - (value - 0.0) / (1.0 - 0.0)))
                        #intensity = max(0, min(255, int(255 * (1 - value / CELL_DENSITY))))
                        intensity = max(0, min(255, intensity))
                        color = (intensity, intensity, intensity)
                    elif mode == "ux":
                        # Wizualizacja prędkości poziomej (u_x) - czerwona dla dodatnich, niebieska dla ujemnych
                        intensity = max(0, min(255, int(255 * abs(value))))
                        if value > 0:
                            color = (255, 255 - intensity, 255 - intensity)  # Czerwona gradacja dla dodatnich
                        else:
                            color = (255 - intensity, 255 - intensity, 255)  # Niebieska gradacja dla ujemnych
                    elif mode == "uy":
                        # Wizualizacja prędkości pionowej (u_y) - czerwona dla dodatnich, niebieska dla ujemnych
                        intensity = max(0, min(255, int(255 * abs(value))))
                        if value > 0:
                            color = (255, 255 - intensity, 255 - intensity)  # Czerwona gradacja dla dodatnich
                        else:
                            color = (255 - intensity, 255 - intensity, 255)  # Niebieska gradacja dla ujemnych

                pygame.draw.rect(
                    self.screen, color,
                    (self.x_offset + j * CELL_SIZE, i * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                )
        self.draw_grid_and_menu_boundary()


    def update(self, speed, mode):
        self.draw_grid(mode)

        # Rysowanie przycisków
        self.draw_button(self.start_button, "Start", BLUE, LIGHT_BLUE)
        self.draw_button(self.stop_button, "Stop", BLUE, LIGHT_BLUE)
        self.draw_button(self.reset_button, "Reset", BLUE, LIGHT_BLUE)

        self.draw_button(self.faster_button, "+", BLUE, LIGHT_BLUE)
        self.draw_button(self.slower_button, "-", BLUE, LIGHT_BLUE)
        self.draw_speed(speed)  # Wyświetl prędkość
       # pygame.display.flip()
