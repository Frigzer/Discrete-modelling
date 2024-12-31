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
        self.start_button = pygame.Rect(70, GRID_HEIGHT * CELL_SIZE + 20, 70, 30)
        self.stop_button = pygame.Rect(220, GRID_HEIGHT * CELL_SIZE + 20, 70, 30)
        self.constant_button = pygame.Rect(420, GRID_HEIGHT * CELL_SIZE + 20, 120, 30)
        self.custom_button = pygame.Rect(420, GRID_HEIGHT * CELL_SIZE + 60, 120, 30)
        self.bounce_back_button = pygame.Rect(420, GRID_HEIGHT * CELL_SIZE + 140, 120, 30)

        self.faster_button = pygame.Rect(630, GRID_HEIGHT * CELL_SIZE + 35, 30, 30)
        self.slower_button = pygame.Rect(770, GRID_HEIGHT * CELL_SIZE + 35, 30, 30)

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


    def update(self, speed, iteration, boundary_condition, mode):
        self.draw_grid(mode)

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

        self.draw_boundary_condition_type(boundary_condition)
       # pygame.display.flip()
