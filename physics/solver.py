from .solarsandbox import SolarSystem, CelestialBody
from scipy.integrate import RK45
import numpy as np

class SimulationSolver:
    def __init__(self, solarSystem: SolarSystem, time_bound=24*3600*700, time_step=3600):
        self.solarSystem = solarSystem
        self.time_bound = time_bound
        self.time_step = time_step

    def reset_body(self, body: CelestialBody):
        body.detach_solver()
        rk45 = RK45(lambda t, y: self.__f(body, t, y), 0, body.get_state(), self.time_bound, self.time_step)
        body.attach_solver(rk45)

    def reset_all(self):
        for body in self.solarSystem.bodies():
            self.reset_body(body)

    def __f(self, body, _, Y):
        x, y = self.solarSystem.get_interactions_field_from_all(body)
        return [x, Y[0], y, Y[2]]

    def solve_step(self):
        bodies = self.solarSystem.bodies()
        collisions = np.zeros((len(bodies), len(bodies)))
        for i in range(len(bodies)):  # detecting collisions
            for j in range(i + 1, len(bodies)):
                if bodies[i].does_collide_with(bodies[j]):
                    collisions[i, j], collisions[j, i] = 1, 1
        for i in range(len(bodies)):  # managing collisions
            collisions_i = [bodies[j] for j in range(i, len(bodies)) if collisions[i, j] == 1]
            if collisions_i != []:
                self.solarSystem.manage_collisions(collisions_i)
        for body in self.solarSystem.bodies():
            if body.solver is not None:
                body.solver.step()
                body.update((body.solver.y[1], body.solver.y[3]), (body.solver.y[0], body.solver.y[2]))
                if body.solver.status == "finished":
                    body.detach_solver()
            else:
                self.reset_body(body)



