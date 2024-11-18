# fire_simulation_logic.py

import numpy as np
import random
from PIL import Image

from fontTools.merge.util import current_time

'''
    0 - ziemia
    1 - drzewo iglaste
    2 - podpalone drzewo
    3 - palace sie drzewo
    4 - spalone drzewo
    5 - woda
    6 - nowe drzewo
    7 - drzewo liściaste
    8 - dziura
    
'''


def convert_image_to_grid(image_path, grid_height, grid_width):
    # Wczytaj obraz
    image = Image.open(image_path)

    # Przeskaluj obraz do rozmiaru siatki
    image = image.resize((grid_width, grid_height))

    # Konwertuj obraz do trybu RGB
    image = image.convert("RGB")

    # Pobierz piksele jako numpy array
    pixel_data = np.array(image)

    # Zainicjuj siatkę symulacji
    grid = np.zeros((grid_height, grid_width), dtype=int)

    # Mapowanie kolorów
    for x in range(grid_height):
        for y in range(grid_width):
            r, g, b = pixel_data[x, y]

            # Jeśli piksel jest ciemnoniebieski (woda)
            if b > g and b > r and b - max(r, g) > 20:
                grid[x, y] = 5  # Woda
            # Jeśli piksel jest zielony (drzewa)
            elif g > r and g > b:
                if g > 100:
                    grid[x, y] = 1  # drzewo iglaste
                else:
                    grid[x, y] = 7  # drzewo liściaste
            # Pozostałe kolory jako ziemia
            else:
                # Dla wietnamu
                if image_path == "wietnam.png":
                    grid[x, y] = 5  # woda
                else:
                    grid[x, y] = 0  # ziemia

    return grid

def initialize_grid(height, width, initial_state="random"):

    grid = np.random.choice([1, 7], size=(height, width), p=[0.5, 0.5])

    if initial_state == "test_random":
        grid = np.random.choice([0, 1, 7], size=(height, width), p=[0.3, 0.35, 0.35])

    elif initial_state == "test_plain":
        grid = np.random.choice([1, 7], size=(height, width), p=[0.5, 0.5])
    elif initial_state == "test_river":
        for i in range(min(height, width)):
            grid[i, i] = 5
            if i + 1 < width:
                grid[i, i + 1] = 5  # Szerokość rzeki
    elif initial_state == "map_1":
        grid = convert_image_to_grid("1.png", grid_height=height, grid_width=width)
    elif initial_state == "map_2":
        grid = convert_image_to_grid("2.png", grid_height=height, grid_width=width)
    elif initial_state == "map_3":
        grid = convert_image_to_grid("3.jpg", grid_height=height, grid_width=width)
    elif initial_state == "map_4":
        grid = convert_image_to_grid("4.png", grid_height=height, grid_width=width)
    elif initial_state == "wietnam":
        grid = convert_image_to_grid("wietnam.png", grid_height=height, grid_width=width)

    return grid

def get_neighbors(grid, x, y, boundary="reflective"):
    height, width = grid.shape
    neighbors = []

    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, 1), (1, -1)]:  # Sąsiedzi (góra, dół, lewo, prawo)
        nx, ny = x + dx, y + dy

        if boundary == "reflective":
            if 0 <= nx < height and 0 <= ny < width:
                neighbors.append((nx, ny))
        elif boundary == "periodic":
            neighbors.append((nx % height, ny % width))

    return neighbors

def fire_simulation_step(grid, regeneration_queue, boundary="periodic", wind_direction=None, humidity=0.5, wind_strength=0.2, cooldown=5, current_iteration=0, random_delay=20):
    new_grid = grid.copy()
    new_regeneration_queue = []
    height, width = grid.shape
    humidity = 1.0 - humidity
    wind_strength = 0.5 - wind_strength

    wind_effect = {
        "N": [(-1, 0), (-1, -1), (-1, 1)],  # Północ i sąsiednie komórki
        "S": [(1, 0), (1, -1), (1, 1)],  # Południe
        "E": [(0, 1), (-1, 1), (1, 1)],  # Wschód
        "W": [(0, -1), (-1, -1), (1, -1)],  # Zachód
        "NE": [(-1, 1), (-1, 0), (0, 1)],  # Północny-wschód
        "NW": [(-1, -1), (-1, 0), (0, -1)],  # Północny-zachód
        "SE": [(1, 1), (1, 0), (0, 1)],  # Południowy-wschód
        "SW": [(1, -1), (1, 0), (0, -1)],  # Południowy-zachód
        None: [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, 1), (-1, -1), (1, 1), (1, -1)],  # Wszystkie kierunki
    }

    # Procesuj regenerację drzew z kolejki
    for (x, y, regen_time) in regeneration_queue:
        if grid[x, y] == 4:  # Sprawdź, czy nadal jest spalone drzewo
            if current_iteration >= regen_time:
                new_grid[x, y] = 6  # Rozpocznij regenerację
            else:
                new_regeneration_queue.append((x, y, regen_time))

    # Pobierz przesunięcia dla wybranego kierunku wiatru
    wind_offsets = wind_effect.get(wind_direction, wind_effect[None])

    for x in range(height):
        for y in range(width):
            if grid[x, y] == 2:  # Początkowe spalanie
                neighbors = get_neighbors(grid, x, y, boundary=boundary)
                if any(grid[nx, ny] == 5 for nx, ny in neighbors):
                    chance = 0.5
                    if random.random() < chance:
                        new_grid[x, y] = 4
                        regen_time = current_iteration + cooldown * humidity + random.randint(0, random_delay)
                        new_regeneration_queue.append((x, y, regen_time))
                    else:
                        new_grid[x, y] = 1 if random.random() < 0.5 else 7
                else:
                    new_grid[x, y] = 3  # Przechodzi do intensywnego spalania

            elif grid[x, y] == 3:  # Intensywne spalanie
                neighbors = get_neighbors(grid, x, y, boundary=boundary)
                if any(grid[nx, ny] == 5 for nx, ny in neighbors):
                    chance = 0.5
                    if random.random() < chance:
                        new_grid[x, y] = 4
                        regen_time = current_iteration + cooldown * humidity + random.randint(0, random_delay)
                        new_regeneration_queue.append((x, y, regen_time))
                    else:
                        new_grid[x, y] = 1 if random.random() < 0.5 else 7
                else:
                    new_grid[x, y] = 4  # Staje się spalone
                    # Dodaj spalone drzewo do kolejki regeneracji
                    regen_time = current_iteration + cooldown + random.randint(0, random_delay)
                    new_regeneration_queue.append((x, y, regen_time))


            elif grid[x, y] == 6:  # Kiełkujące drzewo
                # Losowo wybierz typ drzewa (1 - iglaste, 7 - liściaste)
                new_grid[x, y] = 1 if random.random() < 0.5 else 7

            elif grid[x, y] == 8:
                neighbors = get_neighbors(grid, x, y, boundary=boundary)
                # Sprawdź, czy któryś z sąsiadów to woda
                if any(grid[nx, ny] == 5 for nx, ny in neighbors):
                    new_grid[x, y] = 5  # Dół zmienia się w wodę

            elif grid[x, y] in [1, 7, 6]:  # Zdrowe drzewo
                for dx, dy in wind_effect[None]:
                    nx, ny = x + dx, y + dy

                    # Obsługa warunków brzegowych
                    if boundary == "periodic":
                        nx %= height
                        ny %= width
                    elif boundary == "reflective":
                        if not (0 <= nx < height and 0 <= ny < width):
                            continue

                    # Jeśli sąsiad płonie
                    if grid[nx, ny] in [2, 3]:
                        # Sprawdź, czy w pobliżu jest woda
                        neighbors = get_neighbors(grid, x, y, boundary)
                        water_nearby = any(grid[wx, wy] == 5 for wx, wy in neighbors)

                        # Jeśli kierunek zgodny z wiatrem (stożek)
                        if (dx, dy) in wind_offsets:
                            chance = humidity if (dx, dy) == wind_offsets[0] else humidity / 2
                            chance = chance * 0.9 if grid[x, y] == 7 else chance
                            # Zmniejsz szansę na zapalenie w pobliżu wody
                            if water_nearby:
                                chance *= 0.5  # Zmniejszona szansa przy wodzie
                            if random.random() < chance:
                                new_grid[x, y] = 2  # Zapala się
                                break
                        else:
                            # Mniejsza szansa w innych kierunkach
                            chance = wind_strength
                            # Zmniejsz szansę na zapalenie w pobliżu wody
                            if water_nearby:
                                chance *= 0.5  # Zmniejszona szansa przy wodzie
                            if random.random() < chance:
                                new_grid[x, y] = 2

    return new_grid, new_regeneration_queue
