# main.py

import pygame

from constants import *
from lbm_visualization import LBMVisualizer
from lbm_logic import LBM


def main():
    # Uruchomienie wizualizacji
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH * 3, WINDOW_HEIGHT))  # Szerokie okno
    pygame.display.set_caption("LBM Fluid flow with boundary conditions - Adam Borek")

    clock = pygame.time.Clock()

    boundary_condition = "constant"

    # Inicjalizacja modelu
    lbm = LBM(height=GRID_HEIGHT, width=GRID_WIDTH, tau=1.0, boundary_condition=boundary_condition)

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
                elif visualizer_density.bounce_back_button.collidepoint(event.pos):
                    lbm = LBM(height=GRID_HEIGHT, width=GRID_WIDTH, tau=1.0, boundary_condition="bounce-back")

                    visualizer_density = LBMVisualizer(lbm, screen, "Density", x_offset=0)
                    visualizer_ux = LBMVisualizer(lbm, screen, "Velocity X", x_offset=WINDOW_WIDTH)
                    visualizer_uy = LBMVisualizer(lbm, screen, "Velocity Y", x_offset=2 * WINDOW_WIDTH)

                    iteration = 0

                    boundary_condition="bounce-back"

                    animating = False
                elif visualizer_density.constant_button.collidepoint(event.pos):
                    lbm = LBM(height=GRID_HEIGHT, width=GRID_WIDTH, tau=1.0, boundary_condition="constant")

                    visualizer_density = LBMVisualizer(lbm, screen, "Density", x_offset=0)
                    visualizer_ux = LBMVisualizer(lbm, screen, "Velocity X", x_offset=WINDOW_WIDTH)
                    visualizer_uy = LBMVisualizer(lbm, screen, "Velocity Y", x_offset=2 * WINDOW_WIDTH)

                    iteration = 0

                    boundary_condition="constant"

                    animating = False
                elif visualizer_density.custom_button.collidepoint(event.pos):
                    lbm = LBM(height=GRID_HEIGHT, width=GRID_WIDTH, tau=1.0, boundary_condition="custom")

                    visualizer_density = LBMVisualizer(lbm, screen, "Density", x_offset=0)
                    visualizer_ux = LBMVisualizer(lbm, screen, "Velocity X", x_offset=WINDOW_WIDTH)
                    visualizer_uy = LBMVisualizer(lbm, screen, "Velocity Y", x_offset=2 * WINDOW_WIDTH)

                    iteration = 0

                    boundary_condition="custom"

                    animating = False
                elif visualizer_density.faster_button.collidepoint(event.pos):
                    speed = min(speed + 1, 50)
                elif visualizer_density.slower_button.collidepoint(event.pos):
                    speed = max(speed - 1, 1)

        if animating:
            for _ in range(speed):
                lbm.step(boundary_condition)  # Obliczenia są wykonywane tylko raz
                iteration += 1

        # Rysowanie trzech wizualizacji obok siebie
        screen.fill(WHITE)
        visualizer_density.update(speed, iteration, boundary_condition, "density")
        visualizer_ux.update(speed, iteration, boundary_condition, "ux")
        visualizer_uy.update(speed, iteration, boundary_condition, "uy")
        pygame.display.flip()

        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
