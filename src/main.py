from typing import List, Tuple, Union
from copy import deepcopy
import numpy as np
from mealpy import Problem, BoolVar
from mealpy.swarm_based.GWO import GWO_WOA

from models.car import Car
from models.racetrack import RaceTrack
from models.f1_simulation import F1Simulation

NUMBER_OF_LAPS=66
car=Car()
racetrack=RaceTrack()
# f1_simulation=F1Simulation(car,racetrack,number_of_laps=66)

class F1OptimizationProblem(Problem):
    def __init__(self, bound=None, minmax='min',car:Car=Car(), racetrack:RaceTrack=RaceTrack(), number_of_laps:int=66, **kwargs):
        self.car=car
        self.racetrack=racetrack
        self.number_of_laps=number_of_laps
        super().__init__(bound, minmax, **kwargs)

    def obj_func(self, x):
        f1_simulation=F1Simulation(deepcopy(self.car),deepcopy(self.racetrack),number_of_laps=self.number_of_laps)
        x_decoded=self.decode_solution(x)
        f1_simulation.initialize_setting(...)
        f1_simulation.race()
        return f1_simulation.score()
    
my_bounds=[
    # ListStringVar list_tyre_setting_all_laps,
    BoolVar(n_vars=NUMBER_OF_LAPS-1,name='list_car_status_will_be_pit'),
    # ListStringVar list_engine_setting_all_stopwatches,
    # ListStringVar list_brake_setting_all_stopwatches
]

problem=F1OptimizationProblem(bound=my_bounds,minmax='min',car=car,racetrack=racetrack,number_of_laps=NUMBER_OF_LAPS)
model=GWO_WOA(epoch=1000,pop_size=100)
model.solve(problem)

print(f"Best agent: {model.g_best}")
print(f"Best solution: {model.g_best.solution}")
print(f"Best accuracy: {model.g_best.target.fitness}")
print(f"Best parameters: {model.problem.decode_solution(model.g_best.solution)}")