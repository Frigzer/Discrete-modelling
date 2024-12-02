import pygame

from constants import *

class LGAVisualizer:
    def __init__(self, lga, screen):
        self.reset_button = None
        self.stop_button = None
        self.start_button = None
        self.lga = lga
        self.screen = screen
        self.initialize()
        self.previous_state = None

    # Rysowanie przycisku
    def draw_button(self, screen, rect, text, color):
        pygame.draw.rect(self.screen, color, rect)
        pygame.draw.rect(self.screen, BLACK, rect, 2)
        font = pygame.font.Font(None, 36)
        text_surf = font.render(text, True, BLACK)
        text_rect = text_surf.get_rect(center=rect.center)
        screen.blit(text_surf, text_rect)

    def draw_grid_and_menu_boundary(self):
        # Ustal miejsce, gdzie ma być granica (pozycja y)
        boundary_y = GRID_HEIGHT * CELL_SIZE

        # Rysowanie linii na granicy między gridem a menu
        pygame.draw.line(self.screen, RED, (0, boundary_y), (WINDOW_WIDTH, boundary_y), 5)

    def draw_grid(self, state):
        for i in range(GRID_HEIGHT):
            for j in range(GRID_WIDTH):
                #if self.previous_state is None or state[i, j] != self.previous_state[i, j]:
                color = BLACK if state[i, j] > 0 else WHITE
                border_color = WHITE
                if self.lga.wall[i, j] == -1:  # Rysowanie ściany
                    color = RED
                    border_color = RED
                pygame.draw.rect(self.screen, color, (j * CELL_SIZE, i * CELL_SIZE, CELL_SIZE, CELL_SIZE))
                #pygame.draw.rect(self.screen, border_color, (j * CELL_SIZE, i * CELL_SIZE, CELL_SIZE, CELL_SIZE), 1)

    def update(self):
        self.screen.fill(WHITE)  # Czyszczenie ekranu
        state = self.lga.get_state()
        self.draw_grid(state)  # Rysowanie siatki


        self.previous_state = state.copy()
        # Rysowanie przycisków
        self.draw_grid_and_menu_boundary()
        self.draw_button(self.screen, self.start_button, "Start", GREY)
        self.draw_button(self.screen, self.stop_button, "Stop", GREY)
        self.draw_button(self.screen, self.reset_button, "Reset", GREY)

    def initialize(self):

        # Przycisk
        position = WINDOW_WIDTH // 4
        self.start_button = pygame.Rect(position, GRID_HEIGHT * CELL_SIZE + 20, 100, 50)
        self.stop_button = pygame.Rect(position + 150, GRID_HEIGHT * CELL_SIZE + 20, 100, 50)
        self.reset_button = pygame.Rect(position + 300, GRID_HEIGHT * CELL_SIZE + 20, 100, 50)

