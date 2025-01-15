import random

class Particle:
    def __init__(self, x, y, mass=None, color=None,  mass_range=(1.0, 5.0)):
        self.x = x
        self.y = y
        self.mass = mass if mass else random.uniform(*mass_range)
        self.color = color if color else self._generate_random_color()  # Kolor zależny od masy
        self.path = [(x, y)]  # Ścieżka cząstki

    def _generate_random_color(self):
        """Generuje losowy kolor RGB."""
        return (
            random.randint(0, 255),  # Losowy czerwony
            random.randint(0, 255),  # Losowy zielony
            random.randint(0, 255)   # Losowy niebieski
        )

    def update_position(self, ux, uy, dt=1.0, velocity_scale=1.0):
        """Aktualizuje pozycję cząstki na podstawie prędkości.

        Args:
            ux: Prędkość w osi x w obecnej pozycji.
            uy: Prędkość w osi y w obecnej pozycji.
            dt: Krok czasowy.
            velocity_scale: Skala przyspieszenia ruchu cząstki.
        """
        self.x += ux * velocity_scale / self.mass
        self.y += uy * velocity_scale / self.mass
        self.path.append((self.x, self.y))  # Dodanie nowej pozycji do ścieżki
