import pygame
import numpy as np
from constants import *

class LBMVisualizer:
    def __init__(self, lbm, screen):
        self.lbm = lbm
        self.screen = screen

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
        pygame.draw.line(self.screen, LIGHT_BLUE, (0, boundary_y), (WINDOW_WIDTH, boundary_y), 2)


    def draw_grid(self):
        density = self.lbm.get_density()
        max_density = CELL_DENSITY
        min_density = 0.0

        num_levels = 60  # Liczba przedziałów/poziomów
        step = (max_density - min_density) / num_levels

        for i in range(self.lbm.height):
            for j in range(self.lbm.width):
                if self.lbm.wall.is_wall(i, j):  # Ściana
                    color = RED
                else:

                    # Mapowanie gęstości na kolor (od białego do czarnego)
                    intensity = int(255 * (1 - (density[i, j] - min_density) / (max_density - min_density)))

                    '''
                    level = int((density[i, j] - min_density) // step)
                    intensity = 255 - (level * (255 // num_levels))  # Szarość dla danego poziomu
                    '''
                    intensity = max(0, min(255, intensity))
                    color = (intensity, intensity, intensity)

                pygame.draw.rect(self.screen, color, (j * CELL_SIZE, i * CELL_SIZE, CELL_SIZE, CELL_SIZE))

    def update(self, speed):
        self.screen.fill(WHITE)  # Czyszczenie ekranu
        self.draw_grid()

        # Rysowanie przycisków
        self.draw_grid_and_menu_boundary()
        self.draw_button(self.start_button, "Start", BLUE, LIGHT_BLUE)
        self.draw_button(self.stop_button, "Stop", BLUE, LIGHT_BLUE)
        self.draw_button(self.reset_button, "Reset", BLUE, LIGHT_BLUE)

        self.draw_button(self.faster_button, "+", BLUE, LIGHT_BLUE)
        self.draw_button(self.slower_button, "-", BLUE, LIGHT_BLUE)
        self.draw_speed(speed)  # Wyświetl prędkość
        pygame.display.flip()
