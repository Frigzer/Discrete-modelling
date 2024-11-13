# game_of_life_logic.py

import numpy as np

def initialize_grid(height, width, initial_state="random"):
    grid = np.zeros((height, width), dtype=int)
    start_x = width // 2
    start_y = height // 2
    pattern_str = None

    if initial_state == "glider":
        grid[start_y + 2][start_x + 2] = 1
        grid[start_y + 2][start_x + 3] = 1
        grid[start_y + 1][start_x + 3] = 1
        grid[start_y + 1][start_x + 4] = 1
        grid[start_y + 3][start_x + 4] = 1
    elif initial_state == "oscillator":
        grid[start_y + 1][start_x + 2] = 1
        grid[start_y + 2][start_x + 2] = 1
        grid[start_y + 3][start_x + 2] = 1
    elif initial_state == "random":
        x = start_x
        y = start_y
        x = 0
        y = 0
        random_area_height = 20
        random_area_width = 20
        random_area_height = height
        random_area_width = width
        random_area  = np.random.choice([0, 1], size=(random_area_height, random_area_width))
        grid[y:y + random_area_height, x:x + random_area_width] = random_area
    elif initial_state == "static":
        grid[start_y + 2][start_x + 1] = 1
        grid[start_y + 1][start_x + 2] = 1
        grid[start_y + 1][start_x + 3] = 1
        grid[start_y + 2][start_x + 4] = 1
        grid[start_y + 3][start_x + 2] = 1
        grid[start_y + 3][start_x + 3] = 1
    elif initial_state == "acorn":
        grid[start_y + 1][start_x + 2] = 1
        grid[start_y + 3][start_x + 1] = 1
        grid[start_y + 3][start_x + 2] = 1
        grid[start_y + 2][start_x + 4] = 1
        grid[start_y + 3][start_x + 5] = 1
        grid[start_y + 3][start_x + 6] = 1
        grid[start_y + 3][start_x + 7] = 1
    elif initial_state == "cap":
        grid[start_y + 1][start_x + 2] = 1
        grid[start_y + 1][start_x + 3] = 1
        grid[start_y + 2][start_x + 1] = 1
        grid[start_y + 3][start_x + 1] = 1
        grid[start_y + 3][start_x + 2] = 1
        grid[start_y + 3][start_x + 3] = 1
        grid[start_y + 3][start_x + 4] = 1
        grid[start_y + 2][start_x + 4] = 1
    elif initial_state == "snake_pit":
        pattern = [
            [0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0],
            [0, 1, 1, 0, 1, 0, 0, 0, 0, 1, 0],
            [1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0],
            [1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0],
            [1, 0, 0, 1, 0, 0, 0, 0, 1, 1, 0],
            [1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1],
            [0, 1, 1, 0, 0, 0, 0, 1, 0, 0, 1],
            [0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1],
            [0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1],
            [0, 1, 0, 0, 0, 0, 1, 0, 1, 1, 0],
            [0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0]
        ]
        for i in range(11):
            for j in range(11):
                grid[start_y + i][start_x + j] = pattern[i][j]
    elif initial_state == "???":
        pattern = [
            [0, 1, 0],
            [1, 1, 0],
            [0, 1, 1]
        ]
        for i in range(3):
            for j in range(3):
                grid[start_y + i][start_x + j] = pattern[i][j]
    elif initial_state == "squares":
        grid[start_y][start_x] = 1
        grid[start_y][start_x + 1] = 1
        grid[start_y][start_x + 2] = 1
        grid[start_y + 1][start_x - 1] = 1
        grid[start_y + 1][start_x + 3] = 1
        grid[start_y + 2][start_x + 3] = 1
        grid[start_y + 3][start_x] = 1
        grid[start_y + 3][start_x + 2] = 1
    elif initial_state == "spaceship":
        pattern_str = "8bo$7bobo$6bo3bo$7b3o$$5b2o3b2o$2b2o3bobo3b2o$2b2o3bobo3b2o$2o5bobo5b2o$4b2obobob2o$o6bobo6bo$3b2o2bobo2b2o$bo2bobo3bobo2bo$b2o11b2o$b2o11b2o$4bo7bo$4b3o3b3o$6bo3bo$3b2obo3bob2o$5b2o3b2o$5bobobobo$$5bo2bo2bo$6b2ob2o$5b2o3b2o$$4bo2b3o2bo$3b11o$3b2obo3bob2o!"
    elif initial_state == "bigger_oscillator":
        pattern_str = "20bo14bo$19b2o2b3o4b3o2b2o$16bo4bobo2bo2bo2bobo4bo$13b4o3b2o4bo2bo4b2o\
                        3b4o$12bo12bo4bo12bo$13b4o2b2o14b2o2b4o$14b2o4bobo10bobo4b2o$21bo12bo$\
                        22b2o8b2o$22bobo6bobo$22bobo2b2o2bobo$23bo3b2o3bo$4bo46bo$3bobo44bobo$\
                        3bob2o42b2obo$3bob2o42b2obo$2b2obo44bob2o$$$bo3bo44bo3bo$2obob2o42b2ob\
                        ob2o$2b2o3bo40bo3b2o$6bob3o34b3obo$b2o5bo2bo32bo2bo5b2o$bo7b2o34b2o7bo\
                        $bo2bo46bo2bo$2b2o48b2o$10b2o32b2o$10b2o32b2o$2b2o48b2o$bo2bo46bo2bo$b\
                        o7b2o34b2o7bo$b2o5bo2bo32bo2bo5b2o$6bob3o34b3obo$2b2o3bo40bo3b2o$2obob\
                        2o42b2obob2o$bo3bo44bo3bo$$$2b2obo44bob2o$3bob2o42b2obo$3bob2o42b2obo$\
                        3bobo44bobo$4bo46bo$23bo3b2o3bo$22bobo2b2o2bobo$22bobo6bobo$22b2o8b2o$\
                        21bo12bo$14b2o4bobo10bobo4b2o$13b4o2b2o14b2o2b4o$12bo12bo4bo12bo$13b4o\
                        3b2o4bo2bo4b2o3b4o$16bo4bobo2bo2bo2bobo4bo$19b2o2b3o4b3o2b2o$20bo14bo!"
    elif initial_state == "4_boats":
        pattern_str = "3bo4b$2bobo3b$bob2o3b$obo2b2ob$b2o2bobo$3b2obob$3bobo2b$4bo!"
    elif initial_state == "wave":
        pattern_str = "4bo17bo17bo$3bobo15bobo15bobo$3bobo15bobo15bobo$3bobo15bobo15bobo4$3bo\
                        bo15bobo15bobo2$2bo3bo13bo3bo13bo3bo$3b3o15b3o15b3o4$b2o3b2o11b2o3b2o\
                        11b2o3b2o$bo5bo11bo5bo11bo5bo$2b5o13b5o13b5o$2bobobo13bobobo13bobobo$b\
                        o5bo11bo5bo11bo5bo$bob3obo11bob3obo11bob3obo$bo5bo11bo5bo11bo5bo$4bo\
                        17bo17bo$4bo17bo17bo$4bo17bo17bo4$o7bo9bo7bo9bo7bo$o7bo9bo7bo9bo7bo!"
    elif initial_state == "glider_gun":
        pattern_str = "24bo11b$22bobo11b$12b2o6b2o12b2o$11bo3bo4b2o12b2o$2o8bo5bo3b2o14b$2o8b\
                        o3bob2o4bobo11b$10bo5bo7bo11b$11bo3bo20b$12b2o!!"
    elif initial_state == "replicator":
        pattern_str = "2b3o$bo2bo$o3bo$o2bob$3o!"
    if pattern_str is not None:
        x, y = start_x, start_y
        count = ""
        for char in pattern_str:
            if char.isdigit():
                count += char
            elif char == 'b':  # Martwa komórka
                x += int(count) if count else 1
                count = ""
            elif char == 'o':  # Żywa komórka
                for _ in range(int(count) if count else 1):
                    grid[y, x] = 1
                    x += 1
                count = ""
            elif char == '$':  # Nowa linia
                y += 1
                x = start_x
                count = ""
            elif char == '!':  # Koniec wzoru
                break

    return grid

def count_neighbors(grid, x, y, boundary="periodic"):
    neighbors = 0
    height, width = grid.shape
    for i in range(-1, 2):
        for j in range(-1, 2):
            if i == 0 and j == 0:
                continue
            nx, ny = x + i, y + j
            if boundary == "periodic":
                nx %= height
                ny %= width
            elif boundary == "reflective":
                if nx < 0 or nx >= height:
                    nx = x
                    #nx = max(0, min(height - 1, x))
                if ny < 0 or ny >= width:
                    ny = y
                    #ny = max(0, min(width - 1, y))

            elif nx < 0 or nx >= height or ny < 0 or ny >= width:
                continue
            neighbors += grid[nx, ny]
    return neighbors

def game_of_life_step(grid, boundary="periodic"):
    new_grid = np.zeros(grid.shape, dtype=int)
    for x in range(grid.shape[0]):
        for y in range(grid.shape[1]):
            neighbors = count_neighbors(grid, x, y, boundary)
            if grid[x, y] == 1:
                new_grid[x, y] = 1 if neighbors == 2 or neighbors == 3 else 0
            else:
                new_grid[x, y] = 1 if neighbors == 3 else 0
                #new_grid[x, y] = 1 if neighbors == 3 or neighbors == 6 else 0 # HighLife rule
    return new_grid
