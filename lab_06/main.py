# main.py

import pygame
import numpy as np

from LGA_GUI import LGA
from logic import streaming

# Kolory
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (200, 200, 200)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Rozmiary komórek i okna
CELL_SIZE = 5
GRID_WIDTH = 200
GRID_HEIGHT = 160
WINDOW_WIDTH = GRID_WIDTH * CELL_SIZE
MENU_HEIGHT = 100  # Obszar menu
WINDOW_HEIGHT = GRID_HEIGHT * CELL_SIZE + MENU_HEIGHT

CELL_DENSITY = 0.1

# Rysowanie przycisku
def draw_button(screen, rect, text, color):
    pygame.draw.rect(screen, color, rect)
    pygame.draw.rect(screen, BLACK, rect, 2)
    font = pygame.font.Font(None, 36)
    text_surf = font.render(text, True, BLACK)
    text_rect = text_surf.get_rect(center=rect.center)
    screen.blit(text_surf, text_rect)


# Wizualizacja w pygame
def run_simulation():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Lattice Gas Automata - Pygame Visualization")
    clock = pygame.time.Clock()

    # Przycisk
    start_button = pygame.Rect(50, GRID_HEIGHT * CELL_SIZE + 20, 100, 50)
    stop_button = pygame.Rect(200, GRID_HEIGHT * CELL_SIZE + 20, 100, 50)
    reset_button = pygame.Rect(350, GRID_HEIGHT * CELL_SIZE + 20, 100, 50)

    # Inicjalizacja modelu
    lga = LGA(height=GRID_HEIGHT, width=GRID_WIDTH, density=CELL_DENSITY)

    running = True
    animating = False

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.collidepoint(event.pos):
                    animating = True
                elif stop_button.collidepoint(event.pos):
                    animating = False
                elif reset_button.collidepoint(event.pos):
                    lga = LGA(height=GRID_HEIGHT, width=GRID_WIDTH, density=CELL_DENSITY)
                    animating = False

        if animating:
            lga.step()

        # Rysowanie
        screen.fill(WHITE)
        state = lga.get_state()
        for i in range(GRID_HEIGHT):
            for j in range(GRID_WIDTH):
                color = BLACK if state[i, j] > 0 else WHITE
                if lga.wall[i, j] == -1:  # Rysowanie ściany
                    color = RED
                pygame.draw.rect(screen, color, (j * CELL_SIZE, i * CELL_SIZE, CELL_SIZE, CELL_SIZE))
                #pygame.draw.rect(screen, RED, (j * CELL_SIZE, i * CELL_SIZE, CELL_SIZE, CELL_SIZE), 1)

        # Rysowanie przycisków
        draw_button(screen, start_button, "Start", GREEN)
        draw_button(screen, stop_button, "Stop", BLUE)
        draw_button(screen, reset_button, "Reset", RED)

        pygame.display.flip()
        clock.tick(10)

    pygame.quit()


def main():
    # Uruchomienie wizualizacji
    run_simulation()

if __name__ == "__main__":
    main()
