import numpy as np

from physics import configs
from utils import constants
from physics.solarsandbox import SolarSystem, Star, Planet
from gui.ui import SolarSystemWindow

if __name__ == '__main__':
    solar_system = SolarSystem(configs.clone(configs.SOLAR_SYSTEM))
    window = SolarSystemWindow(solar_system)

    window.start_loop()