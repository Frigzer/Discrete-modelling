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

        #self.initialize_particles(10)

    def initialize_particles(self, num_particles=5, y_min=2, y_max=None):
        """Inicjalizuje cząstki w określonym zakresie wysokości.

        Args:
            num_particles: Liczba cząstek do zainicjowania.
            y_min: Minimalny indeks siatki, gdzie mogą być cząstki (domyślnie 10).
            y_max: Maksymalny indeks siatki, gdzie mogą być cząstki (domyślnie wysokość siatki - 10).
        """
        if y_max is None:
            y_max = self.lbm.height - 2  # Domyślnie 10 komórek od dołu

        self.particles = []
        for i in range(num_particles):
            x = 1  # Start cząstek blisko lewej krawędzi
            y = y_min + i * (y_max - y_min) // num_particles  # Równomierne rozmieszczenie w pionie
            self.particles.append(Particle(x, y))

    def update_particles(self, velocity_scale=100.0):
        """Aktualizuje pozycje cząstek na podstawie prędkości w siatce."""
        for particle in self.particles:
            # Zaokrąglamy pozycję do najbliższej komórki siatki
            grid_x = int(particle.x)
            grid_y = int(particle.y)

            # Sprawdzamy, czy cząstka znajduje się w obrębie siatki
            if 0 <= grid_x < self.lbm.width and 0 <= grid_y < self.lbm.height:
                ux = self.lbm.get_velocity_x()[grid_y, grid_x]
                uy = self.lbm.get_velocity_y()[grid_y, grid_x]
                particle.update_position(ux, uy, velocity_scale=velocity_scale)

    def draw_particles(self):
        """Rysuje ścieżki i pozycje cząstek."""
        for particle in self.particles:
            # Rysowanie ścieżki cząstki
            for i in range(1, len(particle.path)):
                x1, y1 = particle.path[i - 1]
                x2, y2 = particle.path[i]
                pygame.draw.line(
                    self.screen, (0, 255, 255),
                    (self.x_offset + x1 * CELL_SIZE, y1 * CELL_SIZE),
                    (self.x_offset + x2 * CELL_SIZE, y2 * CELL_SIZE), 2
                )

            # Rysowanie aktualnej pozycji cząstki
          #  pygame.draw.circle(
          #      self.screen, (255, 165, 0),  # Niebieski kolor
          #      (int(self.x_offset + particle.x * CELL_SIZE), int(particle.y * CELL_SIZE)), 3
          #  )

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
        """Zapisuje widok tylko gridu jako pliki BMP dla gęstości, ux i uy."""
        modes = ["density", "ux", "uy"]
        for mode in modes:
            self.draw_grid(mode)  # Narysowanie gridu w trybie
            # Wyznaczenie obszaru gridu

            if mode in ["ux", "uy"]:
                self.draw_streamlines(mode=mode, scale=100)  # Linie toku
                self.lbm.draw_particles(self.screen, self.x_offset)  # Cząstki

            grid_rect = pygame.Rect(
                self.x_offset + 2,  # +1 aby pominąć ramkę po lewej
                2,  # +1 aby pominąć ramkę na górze
                self.lbm.width * CELL_SIZE - 2,  # -2 aby pominąć ramki z prawej
                self.lbm.height * CELL_SIZE - 2  # -2 aby pominąć ramkę na dole
            )
            #grid_rect = pygame.Rect(self.x_offset, 0, self.lbm.width * CELL_SIZE, self.lbm.height * CELL_SIZE)
            grid_surface = self.screen.subsurface(grid_rect)  # Wycięcie gridu z ekranu
            grid_array = surfarray.array3d(grid_surface)
            # Konwersja osi do formatu zgodnego z PIL
            grid_array = grid_array.transpose([1, 0, 2])  # Zamiana (x, y, kolor) na (y, x, kolor)
            # Tworzenie obrazu PIL i zapisywanie jako BMP
            img = Image.fromarray(grid_array)
            img.save(f"{base_filename}_{mode}.bmp")

    def load_visualization_from_bmp(self, filename="grid.bmp"):
        """Wczytuje obraz siatki z pliku BMP."""
        # Wczytanie obrazu
        img = Image.open(filename)
        grid_array = np.array(img)

        # Konwersja osi do formatu zgodnego z Pygame
        grid_array = grid_array.transpose([1, 0, 2])  # Zamiana (y, x, kolor) na (x, y, kolor)

        # Aktualizacja ekranu w obszarze siatki
        grid_surface = pygame.surfarray.make_surface(grid_array)
        grid_rect = pygame.Rect(self.x_offset, 0, self.lbm.width * CELL_SIZE, self.lbm.height * CELL_SIZE)
        self.screen.blit(grid_surface, grid_rect)
        print(f"Grid wczytany z pliku {filename}.")

    def save_density_as_bmp(self, filename="density_grid.bmp"):
        """Zapisuje dane gęstości jako obraz BMP w skali szarości."""
        rho = self.lbm.get_rho()  # Pobranie danych gęstości
        intensity = (255 * (1 - (rho / np.max(rho)))).clip(0, 255).astype(np.uint8)
        img = Image.fromarray(intensity, mode="L")
        img.save(filename)
        print(f"Gęstość zapisana do pliku {filename}.")

    def save_velocity_as_bmp(self, velocity, filename="velocity_grid.bmp"):
        """Zapisuje dane prędkości jako obraz BMP w formacie RGB."""
        max_speed = MAX_SPEED
        intensity = (255 * np.abs(velocity) / max_speed).clip(0, 255).astype(np.uint8)
        red_channel = (velocity > 0) * intensity
        blue_channel = (velocity < 0) * intensity
        green_channel = np.zeros_like(intensity, dtype=np.uint8)
        img = Image.merge("RGB", (
            Image.fromarray(red_channel),
            Image.fromarray(green_channel),
            Image.fromarray(blue_channel)
        ))
        img.save(filename)
        print(f"Prędkość zapisana do pliku {filename}.")

    def load_density_from_bmp(self, filename="density_grid.bmp"):
        """Wczytuje dane gęstości z obrazu BMP w skali szarości."""
        img = Image.open(filename).convert("L")
        intensity = np.array(img).astype(np.float32)
        max_rho = np.max(self.lbm.get_rho())
        self.lbm.rho = max_rho * (1 - (intensity / 255))
        print(f"Gęstość wczytana z pliku {filename}.")

    def load_velocity_from_bmp(self, filename="velocity_grid.bmp"):
        """Wczytuje dane prędkości z obrazu BMP w formacie RGB."""
        img = Image.open(filename).convert("RGB")
        img_array = np.array(img)
        red_channel = img_array[..., 0].astype(np.float32)
        blue_channel = img_array[..., 2].astype(np.float32)
        max_speed = MAX_SPEED
        self.lbm.ux = max_speed * (red_channel - blue_channel) / 255
        self.lbm.uy = np.zeros_like(self.lbm.ux)  # Jeśli obsługujesz tylko jedno pole prędkości
        print(f"Prędkość wczytana z pliku {filename}.")
