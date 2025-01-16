import random

class Particle:
    def __init__(self, x, y, mass=None, color=None,  mass_range=(1.0, 5.0)):
        self.x = x
        self.y = y
        self.mass = mass if mass else random.uniform(*mass_range)
        self.color = color if color else self._generate_random_color()
        self.path = [(x, y)]  # Ścieżka cząstki

    def _generate_random_color(self):
        return (
            random.randint(0, 255),  # Losowy czerwony
            random.randint(0, 255),  # Losowy zielony
            random.randint(0, 255)   # Losowy niebieski
        )

    def update_position(self, ux, uy, dt=1.0, velocity_scale=1.0):

        self.x += ux * velocity_scale / self.mass
        self.y += uy * velocity_scale / self.mass
        self.path.append((self.x, self.y))  # Dodanie nowej pozycji do ścieżki
