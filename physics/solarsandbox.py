from tkinter import X, LEFT, RIGHT

import numpy as np
from customtkinter import CTkEntry, CTkLabel, CTkFrame

from utils import constants


class BodyGraphics:
    def __init__(self):
        self.canvas_object = None
        self.trajectory_objects = []
        self.trajectory_count = 0
        self.light_sides = []

    def attach_canvas_object(self, canvas_object):
        self.canvas_object = canvas_object

    def has_to_draw_trajectory(self):
        if self.trajectory_count == 140:
            self.trajectory_count = 0
            return True
        self.trajectory_count += 1
        return False

    def add_trajectory(self, obj):
        self.trajectory_objects.append(obj)

    def pop_trajectory(self):
        return self.trajectory_objects.pop(0)

    def has_to_pop_trajectory(self):
        return len(self.trajectory_objects) > 15

class CelestialBody:
    def __init__(self, name, mass, radius, position, velocity, photo):
        self.name = name
        self.mass = mass
        self.radius = radius
        self.position = position
        self.velocity = velocity
        self.position_cache = [self.position]
        self.graphics = BodyGraphics()
        self.solver = None
        self.photo = photo

    def __str__(self):
        return f'{self.name} ({self.position})'

    def update(self, position, velocity):
        self.position = np.array(position)
        self.velocity = np.array(velocity)
        self.position_cache.append(position)
        if len(self.position_cache) > 100:
            self.position_cache.pop(0)
    
    def get_hitbox_radius(self):
        return max(10, self.radius)


    def get_interaction_field_from(self, other):
        return -(self.position - other.position) * constants.G * other.mass / self.get_distance_from(
            other) ** 3

    def get_distance_from(self, other):
        if isinstance(other, CelestialBody):
            return np.linalg.norm(self.position - other.position)
        return np.linalg.norm(self.position - other)

    def does_collide_with(self, other):
        return self.get_distance_from(other) < (self.radius + other.radius) * 1e3

    def attach_solver(self, solver):
        self.solver = solver

    def detach_solver(self):
        self.solver = None

    def get_state(self):
        return [self.velocity[0], self.position[0], self.velocity[1], self.position[1]]

    def get_color(self, solarSystem):
        return 0, 0, 0
    
    def get_info(self, solar_system):
        return "Name: %(name)s \nMass: %(mass)s kg\nRadius: %(radius)s km" % {"name": self.name, "mass": self.mass, "radius": self.radius}

    def get_entry(self, prop, prop_name, tk_parent, update_callback):
        frame = CTkFrame(tk_parent, fg_color="#F6B12D")
        label = CTkLabel(frame, text=prop_name, fg_color="white", width=10, anchor="w", corner_radius=10)
        label.pack(side=LEFT)
        entry = CTkEntry(frame, corner_radius=10, fg_color="gray")
        entry.insert(0, str(getattr(self, prop)))
        entry.bind("<Enter>", lambda event: setattr(self, prop, float(event.widget.get()) if isinstance(getattr(self, prop), (float, int)) else event.widget.get()))
        entry.pack(side=RIGHT, fill=X, expand=True)
        return frame

    def get_entries(self, tk_parent, update_callback):
        entries = []
        for prop, prop_name in [("name", "Name"), ("mass", "Mass"), ("radius", "Radius")]:
            entries.append(self.get_entry(prop, prop_name, tk_parent, update_callback))
        return entries

    def clone(self):
        return CelestialBody(self.name, self.mass, self.radius, self.position, self.velocity, self.photo)

class Planet(CelestialBody):
    def __init__(self, name, mass, radius, position, velocity, albedo, atmosphere, photo):
        super().__init__(name, mass, radius, position, velocity, photo)
        self.albedo = albedo
        self.atmosphere = atmosphere

    def get_equilibrium_temperature(self, solar_system):
        """
        @arg solar_system : instance de la classe SolarSystem contenant les corps célestes
        """
        stars = [body for body in solar_system.bodies() if isinstance(body, Star)]

        if len(stars) == 0:
            return 0
        T_eq = 0
        for star in stars:
            distance = self.get_distance_from(star)
            luminosity = star.get_luminosity()
            T_eq += ((1 - self.albedo) * luminosity / (16 * np.pi * distance ** 2 * constants.sigma)) ** 0.25
        return T_eq

    def get_color(self, solar_system):
        color_factor = (self.get_equilibrium_temperature(solar_system) / 300) * self.albedo
    
        if self.atmosphere == 'CO2':
            r, g, b = 1.0, 1.0 - color_factor, 0.5 + color_factor * 0.5
        elif self.atmosphere == 'N2_O2':
            r, g, b = 0.1 + color_factor * 0.2, 0.5 + color_factor * 0.5, 1.0
        elif self.atmosphere == 'Thin':
            r, g, b = 1.0, 0.5 + color_factor * 0.3, 0.1 + color_factor * 0.1
        elif self.atmosphere == 'CH4':  # Méthane
            r, g, b = 0.9 - color_factor * 0.2, 0.6 + color_factor * 0.3, 0.1
        elif self.atmosphere == 'H2':  # Hydrogène
            r, g, b = 0.7, 0.7, 1.0 - color_factor * 0.5
        elif self.atmosphere == 'SO2':  # Dioxyde de soufre
            r, g, b = 0.8 + color_factor * 0.2, 0.4, 0.2
        else:
            r, g, b = 0.7, 0.7, 0.7  # Couleur grise par défaut
    
        return r, g, b
    
    def get_info(self, solar_system):
        base_info = super().get_info(solar_system)
        equilibrium_temp = self.get_equilibrium_temperature(solar_system)
        planet_info = f"{base_info}\nEquilibrium temperature: {equilibrium_temp:.2f} K"
        return planet_info

    def get_entries(self, tk_parent, update_callback):
        entries = super().get_entries(tk_parent, update_callback)
        albedo_frame = self.get_entry("albedo", "Albedo", tk_parent, update_callback)
        atmosphere_frame = self.get_entry("atmosphere", "Atmosphere", tk_parent, update_callback)
        entries.extend([albedo_frame, atmosphere_frame])
        return entries

    def clone(self):
        return Planet(self.name, self.mass, self.radius, self.position, self.velocity, self.albedo, self.atmosphere, self.photo)


class Star(CelestialBody):
    def __init__(self, name, mass, radius, position, velocity, temperature,photo):
        super().__init__(name, mass, radius, position, velocity,photo)
        self.temperature = temperature

    def get_luminosity(self):
        return 4 * np.pi * (self.radius * 1e3) ** 2 * constants.sigma * self.temperature ** 4

    def get_color(self, _):
        """ Utilise la loi de Wien pour calculer la couleur de l'étoile en fonction de sa température. """
        lambda_max = (2.8977729e-3 / self.temperature)*10**9
        r, g, b = 0, 0, 0
        if 380 <= lambda_max < 440:
            r, g, b = -1 * (lambda_max - 440) / (440 - 380), 0, 1
        elif 440 <= lambda_max < 490:
            r, g, b = 0, (lambda_max - 440) / (490 - 440), 1
        elif 490 <= lambda_max < 510:
            r, g, b = 0, 1, -1 * (lambda_max - 510) / (510 - 490)
        elif 510 <= lambda_max < 580:
            r, g, b = (lambda_max - 510) / (580 - 510), 1, 0
        elif 580 <= lambda_max < 645:
            r, g, b = 1, -1 * (lambda_max - 645) / (645 - 580), 0
        elif 645 <= lambda_max < 780:
            r, g, b = 1, 0, 0
        return r, g, b
    
    def get_info(self, solar_system):
        base_info = super().get_info(solar_system)
        luminosity = self.get_luminosity()
        star_info = f"{base_info}\nLuminosity: {luminosity:.2e} W"
        return star_info

    def get_entries(self, tk_parent, update_callback):
        entries = super().get_entries(tk_parent, update_callback)
        temperature_frame = self.get_entry("temperature", "Temperature", tk_parent, update_callback)
        entries.append(temperature_frame)
        return entries

    def clone(self):
        return Star(self.name, self.mass, self.radius, self.position, self.velocity, self.temperature, self.photo)


class SolarSystem:
    def __init__(self, celestial_bodies):
        self.__celestial_bodies = celestial_bodies

    def add_body(self, body):
        self.__celestial_bodies.append(body)

    def remove_body(self, body):
        self.__celestial_bodies.remove(body)

    def bodies(self) -> list[CelestialBody]:
        return self.__celestial_bodies

    def get_interactions_field_from_all(self, body):
        return np.sum([body.get_interaction_field_from(other) for other in self.__celestial_bodies if other != body],
                      axis=0)

    @staticmethod
    def get_center_of_mass(bodies):
        total_mass = 0
        weighted_positions = np.zeros(2)  # Pour stocker la somme pondérée des positions
        for body in bodies:
            total_mass += body.mass
            weighted_positions += body.mass * body.position

        if total_mass == 0:
            raise ValueError("La masse totale des corps est nulle. Impossible de calculer le centre de masse.")

        # Le centre de masse est la position pondérée par la masse totale
        center_of_mass = weighted_positions / total_mass

        return center_of_mass

    @staticmethod
    def convert_speed(r, a, m=1.989e30):
        return np.sqrt(constants.G * m * (2 / r - 1 / a))

    def manage_collisions(self, bodies):
        most_massive = max(bodies, key=lambda body: body.mass)
        most_massive.mass = sum([body.mass for body in bodies])
        most_massive.velocity = sum([body.mass * body.velocity for body in bodies]) / most_massive.mass
        for body in bodies:
            if body != most_massive:
                self.remove_body(body)

    def convert_coords(self, position, width, height, scale):
        center_of_mass = self.get_center_of_mass(self.__celestial_bodies)
        converted_pos = np.array((0.5 * width, - 0.5 * height)) - (center_of_mass - position) * scale
        return converted_pos[0], - converted_pos[1]

    def revert_coords(self, position, width, height, scale, center=True):
        center_of_mass = SolarSystem.get_center_of_mass(self.__celestial_bodies)
        reverted_pos = (center_of_mass - ((np.array((0.5 * width, - 0.5 * height)) if center else np.array((0, 0))) - np.array(position)) / scale)
        return reverted_pos
