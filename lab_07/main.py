# main.py

import pygame
from constants import *
from lbm_visualization import LBMVisualizer
from lbm_logic import LBM



def main():
    # Uruchomienie wizualizacji
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Lattice Boltzmann Method - Adam Borek")
    clock = pygame.time.Clock()

    # Inicjalizacja modelu
    lbm = LBM(height=GRID_HEIGHT, width=GRID_WIDTH, tau=1.0)


    visualizer = LBMVisualizer(lbm, screen)

    speed = 10
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
                    lbm = LBM(height=GRID_HEIGHT, width=GRID_WIDTH, tau=1.0)
                    visualizer = LBMVisualizer(lbm, screen)
                    animating = False
                    #speed = 10  # Reset prędkości
                elif visualizer.faster_button.collidepoint(event.pos):
                    speed = min(speed + 1, 50)  # Zwiększ prędkość (maks. 50 kroków na iterację)
                elif visualizer.slower_button.collidepoint(event.pos):
                    speed = max(speed - 1, 1)  # Zmniejsz prędkość (min. 1 krok na iterację)


        if animating:
            for _ in range(speed):
                lbm.step()

        # Rysowanie
        visualizer.update(speed)

        #pygame.display.flip()
        clock.tick(360)

    pygame.quit()

if __name__ == "__main__":
    main()
