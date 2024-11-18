import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.patches import Rectangle
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.colors import BoundaryNorm
import tkinter as tk
import random

from numpy import dtype

from fire_simulation_logic import initialize_grid, fire_simulation_step


class FireSimulationGUI:
    def __init__(self, root, height=50, width=50, initial_state="thin_forest", boundary="reflective"):
        self.root = root
        self.height = height
        self.width = width
        self.initial_state = initial_state
        self.boundary = boundary
        self.grid = initialize_grid(height, width, initial_state)
        self.regeneration_queue = []
        self.iteration = 0
        self.anim_running = False

        # Rozmiar okna
        self.root.geometry("1440x900")  # szerokość x wysokość

        # Ustawienia figury i osi
        self.fig, self.ax = plt.subplots(figsize=(10, 8))  # szerokość x wysokość w calach

        self.colors = ["brown", "green", "red", "orange", "black", "blue", "lightgreen", "darkgreen", "grey"]
        self.cmap= ListedColormap(self.colors)
        self.norm = BoundaryNorm([0, 1, 2, 3, 4, 5, 6, 7, 8, 9], len(self.colors))

        self.im = self.ax.imshow(self.grid, cmap=self.cmap, norm=self.norm, animated=True)

        # Dodanie granic siatki
        self.border = Rectangle(
            (-0.5, -0.5), self.width, self.height, linewidth=2, edgecolor="blue", facecolor="none"
        )
        self.ax.add_patch(self.border)

        self.create_gridlines()

        # Tworzenie głównej ramki (kontener)
        main_frame = tk.Frame(root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Ustawienia canvas do rysowania wykresu w Tkinterze
        self.canvas = FigureCanvasTkAgg(self.fig, master=main_frame)
        self.canvas.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Tworzenie ramki po prawej stronie dla kontroli wiatru
        right_frame = tk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)

        # Etykieta "Kierunek wiatru"
        wind_label = tk.Label(right_frame, text="Kierunek wiatru", font=("Arial", 12, "bold"))
        wind_label.pack(pady=5)

        # Wybór kierunku wiatru
        wind_options = ["None", "N", "S", "E", "W", "NE", "NW", "SE", "SW"]
        self.wind_direction_var = tk.StringVar(value="None")
        self.wind_menu = tk.OptionMenu(right_frame, self.wind_direction_var, *wind_options)
        self.wind_menu.config(width=10)
        self.wind_menu.pack(pady=5)

        # Etykieta "Wilgotność powietrza"
        wind_strength_label = tk.Label(right_frame, text="Wilgotność powietrza", font=("Arial", 12, "bold"))
        wind_strength_label.pack(pady=5)

        # Suwak siły wiatru
        self.wind_strength_scale = tk.Scale(right_frame, from_=0.0, to=1.0, resolution=0.1, orient=tk.HORIZONTAL)
        self.wind_strength_scale.set(0.3)  # Domyślna wartość
        self.wind_strength_scale.pack(pady=5)

        # Etykieta "Szansa poza wiatrem"
        low_chance_label = tk.Label(right_frame, text="Siła wiatru w kierunku", font=("Arial", 12, "bold"))
        low_chance_label.pack(pady=5)

        # Suwak szansy zapalenia poza wiatrem
        self.low_chance_scale = tk.Scale(right_frame, from_=0.0, to=0.5, resolution=0.1, orient=tk.HORIZONTAL)
        self.low_chance_scale.set(0.4)  # Domyślna wartość
        self.low_chance_scale.pack(pady=5)

        regeneration_label = tk.Label(right_frame, text="Czas do regeneracji", font=("Arial", 12, "bold"))
        regeneration_label.pack(pady=5)
        self.regeneration_scale = tk.Scale(right_frame, from_=100.0, to=500.0, resolution=1.0, orient=tk.HORIZONTAL)
        self.regeneration_scale.set(250.0)  # Domyślna wartość
        self.regeneration_scale.pack(pady=5)

        # Lista możliwych akcji
        self.action_var = tk.StringVar(value="fire")  # Domyślna akcja to "fire"
        # Nagłówek
        tk.Label(right_frame, text="Wybierz akcję:", font=("Arial", 12, "bold")).pack(anchor=tk.W)

        # Przyciski radiowe
        actions = [
                    ("Napalm", "fire"),
                    ("Gaszenie pożaru", "extinguish"),
                    ("Zasadź drzewo", "tree"),
                    ("Bomba zapalająca", "incendiary_bomb"),
                    ("Kop", "dig"),
                    ("Zetnij drzewo", "chop"),
                    ("Zakop", "cover_up")
                ]
        for text, action in actions:
            tk.Radiobutton(right_frame, text=text, variable=self.action_var, value=action).pack(anchor=tk.W)

        # Tworzenie głównej ramki dla przycisków i opcji
        control_frame = tk.Frame(root)
        control_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

        # Przyciski sterujące
        self.start_button = tk.Button(control_frame, text="Start", command=self.start_animation)
        self.start_button.grid(row=0, column=0, padx=5, pady=5)

        self.pause_button = tk.Button(control_frame, text="Pause", command=self.pause_animation)
        self.pause_button.grid(row=0, column=1, padx=5, pady=5)

        # Wybór stanu początkowego
        self.initial_state_var = tk.StringVar(value="test_plain")
        state_options = ["test_random", "test_plain", "test_river", "map_1", "map_2", "map_3", "map_4", "wietnam"]
        self.state_menu = tk.OptionMenu(control_frame, self.initial_state_var, *state_options)
        self.state_menu.config(width=10)
        tk.Label(control_frame, text="Stan początkowy:").grid(row=0, column=2, padx=5, pady=5)
        self.state_menu.grid(row=0, column=3, padx=5, pady=5)

        self.reset_button = tk.Button(control_frame, text="Reset", command=self.reset_animation)
        self.reset_button.grid(row=0, column=4, padx=5, pady=5)

        # Suwak prędkości
        self.speed_scale = tk.Scale(control_frame, from_=1, to=500, orient=tk.HORIZONTAL, label="Prędkość (ms)")
        self.speed_scale.set(200)
        self.speed_scale.grid(row=0, column=5, padx=5, pady=5)

        # Wybór warunku brzegowego
        self.boundary_var = tk.StringVar(value="reflective")
        boundary_options = ["periodic", "reflective"]
        self.boundary_menu = tk.OptionMenu(control_frame, self.boundary_var, *boundary_options)
        self.boundary_menu.config(width=10)
        tk.Label(control_frame, text="Warunek brzegowy:").grid(row=0, column=6, padx=5, pady=5)
        self.boundary_menu.grid(row=0, column=7, padx=5, pady=5)

        # Etykieta pokazująca aktualny warunek brzegowy
        self.boundary_label = tk.Label(control_frame, text=f"Aktualny warunek: {self.boundary}",
                                       font=("Arial", 10, "italic"))
        self.boundary_label.grid(row=0, column=8, padx=5, pady=5)

        # Etykieta liczby iteracji
        self.iteration_label = tk.Label(control_frame, text=f"Iteracja: {self.iteration}", font=("Arial", 10, "italic"))
        self.iteration_label.grid(row=0, column=9, padx=10, pady=5)

        self.scale_factor = 1.2
        self.mouse_pressed = False

        # Połączenie zdarzeń przybliżania i przesuwania
        self.fig.canvas.mpl_connect("scroll_event", self.zoom)
        #self.fig.canvas.mpl_connect("button_press_event", self.on_click)
        self.step_size = 5  # Ilość komórek przesunięcia
        self.root.bind("<Left>", lambda event: self.move_view("left"))
        self.root.bind("<Right>", lambda event: self.move_view("right"))
        self.root.bind("<Up>", lambda event: self.move_view("up"))
        self.root.bind("<Down>", lambda event: self.move_view("down"))
        self.fig.canvas.mpl_connect("button_press_event", self.on_press)
        self.fig.canvas.mpl_connect("button_release_event", self.on_release)
        self.fig.canvas.mpl_connect("motion_notify_event", self.on_motion)

    def update_frame(self):
        if self.anim_running:
            self.iteration += 1
            wind_direction = self.wind_direction_var.get()
            wind_strength = self.wind_strength_scale.get()
            low_chance = self.low_chance_scale.get()
            regeneration_cooldown = self.regeneration_scale.get()
            self.grid, self.regeneration_queue = fire_simulation_step(self.grid, self.regeneration_queue, self.boundary, wind_direction, wind_strength, low_chance, regeneration_cooldown, self.iteration)
            self.iteration_label.config(text=f"Iteracja: {self.iteration}")
            self.im.set_array(self.grid)
            self.canvas.draw()

            # Odświeżaj co `interval` ms, w zależności od wartości z suwaka prędkości
            interval = self.speed_scale.get()
            self.root.after(interval, self.update_frame)

    def start_animation(self):
        self.anim_running = True
        self.update_frame()  # Startuje ręczna animacja

    def pause_animation(self):
        self.anim_running = False

    def reset_animation(self):
        self.initial_state = self.initial_state_var.get()
        self.boundary = self.boundary_var.get()
        self.grid = initialize_grid(self.height, self.width, self.initial_state)
        self.regeneration_queue = []
        self.iteration = 0
        self.iteration_label.config(text=f"Iteracja: {self.iteration}")
        self.im.set_array(self.grid)
        self.canvas.draw()
        self.boundary_label.config(text=f"Aktualny warunek: {self.boundary}")

    def create_gridlines(self):
        for x in range(self.width + 1):
            self.ax.axvline(x - 0.5, color="white", linestyle="-", linewidth=0.5)
        for y in range(self.height + 1):
            self.ax.axhline(y - 0.5, color="white", linestyle="-", linewidth=0.5)
        self.ax.set_xticks([])
        self.ax.set_yticks([])

    def zoom(self, event):
        if event.button == 'up':
            scale_factor = self.scale_factor
        elif event.button == 'down':
            scale_factor = 1 / self.scale_factor
        else:
            return

        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()

        x_center = event.xdata
        y_center = event.ydata

        # Nowe limity po przybliżeniu/oddaleniu
        new_xlim = [x_center + (x - x_center) * scale_factor for x in xlim]
        new_ylim = [y_center + (y - y_center) * scale_factor for y in ylim]

        self.ax.set_xlim(new_xlim)
        self.ax.set_ylim(new_ylim)
        self.canvas.draw()

    def move_view(self, direction):
        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()

        if direction == "left":
            self.ax.set_xlim(xlim[0] - self.step_size, xlim[1] - self.step_size)
        elif direction == "right":
            self.ax.set_xlim(xlim[0] + self.step_size, xlim[1] + self.step_size)
        elif direction == "up":
            self.ax.set_ylim(ylim[0] - self.step_size, ylim[1] - self.step_size)
        elif direction == "down":
            self.ax.set_ylim(ylim[0] + self.step_size, ylim[1] + self.step_size)

        # Odświeżenie widoku
        self.canvas.draw()

    def on_press(self, event):
        if event.inaxes:
            self.mouse_pressed = True
            self.apply_action(event)

    def on_release(self, event):
        self.mouse_pressed = False

    def on_motion(self, event):
        if self.mouse_pressed and event.inaxes:
            self.apply_action(event)

    def apply_action(self, event):
        if event.inaxes:
            x = int(event.xdata + 0.5)
            y = int(event.ydata + 0.5)

            # Sprawdź, czy współrzędne mieszczą się w siatce
            if 0 <= x < self.width and 0 <= y < self.height:
                # Wykonaj akcję w zależności od wybranej opcji
                action = self.action_var.get()
                if action == "fire" and self.grid[y, x] in [1, 6, 7]:
                    self.grid[y, x] = 2  # Tworzenie ognia
                elif action == "extinguish":
                    if self.grid[y, x] in [2, 3]:
                        self.grid[y, x] = 1 if random.random() < 0.5 else 7  # Gaszenie pożaru (pusta komórka)
                    elif self.grid[y, x] == 8:
                        self.grid[y, x] = 5
                elif action == "tree" and self.grid[y, x] == 0:
                    self.grid[y, x] = 1 if random.random() < 0.5 else 7 # Dodanie drzewa
                elif action == "dig" and self.grid[y, x] == 0:
                    self.grid[y, x] = 8  # Wykopanie dołu
                elif action == "incendiary_bomb":
                    self.trigger_incendiary_bomb(x, y)  # Wywołaj wybuch bomby zapalającej
                    self.mouse_pressed = False
                elif action == "chop" and self.grid[y, x] in [1, 4, 6, 7]:
                    self.grid[y, x] = 0
                elif action == "cover_up" and self.grid[y, x] in [8, 5]:
                    self.grid[y, x] = 0

                # Zaktualizuj wizualizację
                self.im.set_array(self.grid)
                self.canvas.draw()

    def trigger_incendiary_bomb(self, x, y, radius=3):
        for i in range(-radius, radius + 1):
            for j in range(-radius, radius + 1):
                nx, ny = x + i, y + j

                if 0 <= nx < self.width and 0 <= ny < self.height:
                    # Oblicz odległość od centrum i wprowadź losowość do promienia
                    distance = (i ** 2 + j ** 2) ** 0.5
                    random_factor = random.uniform(0.8, 1.2)  # Losowy współczynnik zmieniający kształt
                    adjusted_radius = radius * random_factor

                    if distance <= adjusted_radius:
                        # Wewnątrz centralnego obszaru (losowość dla dziur w kraterze)
                        if random.random() < 0.9:  # 90% szans na centralny obszar
                            self.grid[ny, nx] = 8  # Centralny obszar staje się pusty
                        # Na granicy obszaru (losowość dla płomieni)
                        elif distance <= adjusted_radius and self.grid[ny, nx] in [1, 6, 7]:
                            if random.random() < 0.7:  # 70% szans na zapalenie granicy
                                self.grid[ny, nx] = 2  # Granice zaczynają płonąć