# main.py

import pygame
from constants import *
from lga_visualization import LGAVisualizer
from lga_logic import LGA



def main():
    # Uruchomienie wizualizacji
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Lattice Gas Automata - Adam Borek")
    clock = pygame.time.Clock()

    # Inicjalizacja modelu
    lga = LGA(height=GRID_HEIGHT, width=GRID_WIDTH, density=CELL_DENSITY)

    visualizer = LGAVisualizer(lga, screen)


    running = True
    animating = False

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if visualizer.start_button.collidepoint(event.pos):
                    animating = True
                elif visualizer.stop_button.collidepoint(event.pos):
                    animating = False
                elif visualizer.reset_button.collidepoint(event.pos):
                    lga = LGA(height=GRID_HEIGHT, width=GRID_WIDTH, density=CELL_DENSITY)
                    visualizer = LGAVisualizer(lga, screen)
                    animating = False


        if animating:
            lga.step()

        # Rysowanie
        visualizer.update()

        pygame.display.flip()
        clock.tick(360)

    pygame.quit()

if __name__ == "__main__":
    main()
