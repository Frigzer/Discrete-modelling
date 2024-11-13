import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.patches import Rectangle
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from game_of_life_logic import initialize_grid, game_of_life_step


class GameOfLifeGUI:
    def __init__(self, root, height=50, width=50, initial_state="glider", boundary="periodic"):
        self.root = root
        self.height = height
        self.width = width
        self.initial_state = initial_state
        self.boundary = boundary
        self.grid = initialize_grid(height, width, initial_state)
        self.iteration = 0
        self.anim_running = False

        # Rozmiar okna
        self.root.geometry("1440x900")  # szerokość x wysokość

        # Ustawienia figury i osi
        self.fig, self.ax = plt.subplots(figsize=(10, 8))  # szerokość x wysokość w calach
        self.im = self.ax.imshow(self.grid, cmap=ListedColormap(["white", "black"]), animated=True)

        # Dodanie granic siatki
        self.border = Rectangle(
            (-0.5, -0.5), self.width, self.height, linewidth=2, edgecolor="red", facecolor="none"
        )
        self.ax.add_patch(self.border)

        self.create_gridlines()

        # Ustawienia canvas do rysowania wykresu w Tkinterze
        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas.get_tk_widget().pack(pady=10)

        # Tworzenie głównej ramki dla przycisków i opcji
        control_frame = tk.Frame(root)
        control_frame.pack(pady=10)

        # Przyciski sterujące
        self.start_button = tk.Button(control_frame, text="Start", command=self.start_animation)
        self.start_button.grid(row=0, column=0, padx=5, pady=5)

        self.pause_button = tk.Button(control_frame, text="Pause", command=self.pause_animation)
        self.pause_button.grid(row=0, column=1, padx=5, pady=5)

        # Wybór stanu początkowego
        self.initial_state_var = tk.StringVar(value="glider")
        state_options = ["glider", "oscillator", "random", "static", "acorn", "cap", "snake_pit", "???", "squares", "spaceship", "bigger_oscillator", "4_boats", "wave", "glider_gun", "replicator"]
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
        self.boundary_var = tk.StringVar(value="periodic")
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

        # Przybliżanie i przesuwanie ekranu
        self.scale_factor = 1.2
        self.press = None  # pozycja początkowa dla przesuwania

        # Połączenie zdarzeń przybliżania i przesuwania
        self.fig.canvas.mpl_connect("scroll_event", self.zoom)
        self.fig.canvas.mpl_connect("button_press_event", self.on_press)
        self.fig.canvas.mpl_connect("button_release_event", self.on_release)
        self.fig.canvas.mpl_connect("motion_notify_event", self.on_motion)

    def update_frame(self):
        if self.anim_running:
            self.grid = game_of_life_step(self.grid, self.boundary)
            self.iteration += 1
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

    def on_press(self, event):
        if event.inaxes:
            self.press = (event.xdata, event.ydata)

    def on_release(self, event):
        self.press = None

    def on_motion(self, event):
        if self.press is None or not event.inaxes:
            return

        x_prev, y_prev = self.press
        dx = x_prev - event.xdata
        dy = y_prev - event.ydata

        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()

        self.ax.set_xlim([x + dx for x in xlim])
        self.ax.set_ylim([y + dy for y in ylim])

        self.canvas.draw()

        # Aktualizuje pozycję kliknięcia
        self.press = (event.xdata, event.ydata)
