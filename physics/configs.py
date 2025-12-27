import numpy as np

from physics.solarsandbox import Planet, Star, SolarSystem, CelestialBody


def clone(config):
    return [body.clone() for body in config]


SOLAR_SYSTEM = [
    Star('Sun', 1.989e30, 696340, np.array([0, 0]), np.array([0, 0]), 5000, './assets/Soleil.png'),
    Planet('Mercury', 3.285e23, 2439, np.array([4.6e10, 0]), np.array([0, SolarSystem.convert_speed(4.6e10, 5.791e10)]),
           0.3, "CO2", './assets/Mercure.png'),
    Planet('Venus', 4.867e24, 6052, np.array([1.074e11, 0]),
           np.array([0, SolarSystem.convert_speed(1.074e11, 1.082e11)]), 0.3, "CO2", './assets/Venus.png'),
    Planet('Earth', 5.97e24, 6371, np.array([1.496e11, 0]), np.array([0, SolarSystem.convert_speed(1.47e11, 1.496e11)]),
           0.3, "H2", './assets/Terre.png'),
    Planet('Mars', 6.42e23, 3389, np.array([2.279e11, 0]), np.array([0, SolarSystem.convert_speed(2.067e11, 2.279e11)]),
           0.3, "CO2", './assets/Mars.png'),
    Planet('Jupiter', 1.898e27, 69911, np.array([7.785e11, 0]),
           np.array([0, SolarSystem.convert_speed(7.405e11, 7.785e11)]), 0.3, "CO2", './assets/Jupiter.png'),
    Planet('Saturn', 5.683e26, 58232, np.array([1.4335e12, 0]),
           np.array([0, SolarSystem.convert_speed(1.35255e12, 1.4335e12)]), 0.3, "CO2", './assets/Saturne.png'),
    Planet('Uranus', 8.681e25, 25365, np.array([2.8707e12, 0]),
           np.array([0, SolarSystem.convert_speed(2.735e12, 28707e12)]), 0.3, "CO2", './assets/Uranus.png'),
    Planet('Neptune', 1.0243e26, 24622, np.array([4.4984e12, 0]),
           np.array([0, SolarSystem.convert_speed(4.4598e12, 4.4984e12)]), 0.3, "CO2", './assets/Neptune.png'),
    Planet('Pluto', 1.314e22, 1185, np.array([5.9008e12, 0]),
           np.array([0, SolarSystem.convert_speed(4.436e12, 5.9008e12)]), 0.3, "H2", './assets/Pluton.png')
]

EARTH_MOON = [
    Planet('Earth', 5.97e24, 6371, np.array([0, 0]), np.array([0, 0]),
           0.3, "H2", './assets/Terre.png'),
    Planet('Moon', 7.342e22, 1737, np.array([3.626e8, 0]),
                  np.array([0, SolarSystem.convert_speed(3.626e8, 3.847e8, 5.97e24)]), 0.3, "CO2", './assets/Lune.png')
]

EARTH_MOON_SUN = [
    Star('Sun', 1.989e30, 696340, np.array([0, 0]), np.array([0, 0]), 5000, './assets/Soleil.png'),
    Planet('Earth', 5.97e24, 6371, np.array([1.496e11, 0]), np.array([0, SolarSystem.convert_speed(1.47e11, 1.496e11)]),
           0.3, "H2", './assets/Terre.png'),
    Planet('Moon', 7.342e22, 1737, np.array([1.496e11 + 3.626e8, 0]), np.array([0, SolarSystem.convert_speed(1,1)]) +
                  np.array([0, SolarSystem.convert_speed(3.626e8, 3.847e8, 5.97e24)]), 0.3, "CO2", './assets/Lune.png')
]

KEPLER = [
       Star('Kepler-16 A', 1.37241e30, 451925, np.array([0,0]), np.array([0, 0]), 4850, None),
       Star('Kepler-16 B', 0.403767e30, 157372, np.array([6.7112596753e10, 0]), np.array([0, 40661]), 4000, None),      
       Planet('Kepler-16 (AB) b',0.6322338e27, 53890, np.array([5.05436579269e11, 0]), np.array([0, 22700]), 0, False, None)

]

EMPTY = []

CONFIGURATIONS = {
    "Solar System": SOLAR_SYSTEM,
    "Kepler-16": KEPLER,
    "Earth-Moon": EARTH_MOON,
    "Earth-Moon-Sun": EARTH_MOON_SUN,
    "Empty": EMPTY
}
