# main.py

import pygame
from Tools.demo.sortvisu import steps

from constants import *
from lbm_visualization import LBMVisualizer
from lbm_logic import LBM


def main():
    # Uruchomienie wizualizacji
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH * 3, WINDOW_HEIGHT))  # Szerokie okno
    pygame.display.set_caption("LBM Visualization - Density | Velocity X | Velocity Y")

    clock = pygame.time.Clock()

    # Inicjalizacja modelu
    lbm = LBM(height=GRID_HEIGHT, width=GRID_WIDTH, tau=1.0)

    # Jeden wizualizator, ale z trzema różnymi "trybami" wizualizacji
    visualizer_density = LBMVisualizer(lbm, screen, "Density", x_offset=0)
    visualizer_ux = LBMVisualizer(lbm, screen, "Velocity X", x_offset=WINDOW_WIDTH)
    visualizer_uy = LBMVisualizer(lbm, screen, "Velocity Y", x_offset=2 * WINDOW_WIDTH)


    speed = 1
    running = True
    animating = False
    iteration = 0

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if visualizer_density.start_button.collidepoint(event.pos):
                    animating = True
                    #lbm.step()
                elif visualizer_density.stop_button.collidepoint(event.pos):
                    animating = False
                elif visualizer_density.reset_button.collidepoint(event.pos):
                    lbm = LBM(height=GRID_HEIGHT, width=GRID_WIDTH, tau=1.0)

                    visualizer_density = LBMVisualizer(lbm, screen, "Density", x_offset=0)
                    visualizer_ux = LBMVisualizer(lbm, screen, "Velocity X", x_offset=WINDOW_WIDTH)
                    visualizer_uy = LBMVisualizer(lbm, screen, "Velocity Y", x_offset=2 * WINDOW_WIDTH)

                    iteration = 0

                    animating = False

                elif visualizer_density.faster_button.collidepoint(event.pos):
                    speed = min(speed + 1, 50)
                elif visualizer_density.slower_button.collidepoint(event.pos):
                    speed = max(speed - 1, 1)

        if animating:
            for _ in range(speed):
                lbm.step()  # Obliczenia są wykonywane tylko raz
                iteration += speed

        # Rysowanie trzech wizualizacji obok siebie
        screen.fill(WHITE)
        visualizer_density.update(speed, iteration, "density")
        visualizer_ux.update(speed, iteration, "ux")
        visualizer_uy.update(speed, iteration, "uy")
        pygame.display.flip()

        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
