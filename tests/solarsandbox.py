import numpy as np
import pytest

from physics.solarsandbox import Star, Planet, SolarSystem


def test_coord_conversion():
    bodies = [
        Star('Soleil', 1.989e30, 696340, np.array([0, 0]), np.array([0, 0]), 5000),
        Planet('Terre', 5.97e24, 6371, np.array([1.496e11, 0]), np.array([0, 0]), 0.3, 'H2'),
    ]
    solar_system = SolarSystem(bodies)
    height = 700
    width = 1200
    scale = 1e-11

    assert solar_system.convert_coords(solar_system.revert_coords(bodies[1].position, width, height, scale), width, height, scale) == (bodies[1].position[0], bodies[1].position[1])


