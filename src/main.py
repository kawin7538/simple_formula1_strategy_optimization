from typing import List, Tuple, Union
from copy import deepcopy
from mealpy import Problem, BoolVar, StringVar, MixedSetVar
from mealpy.swarm_based.GWO import GWO_WOA, IGWO, OriginalGWO
from mealpy.swarm_based.PSO import HPSO_TVAC
from mealpy.swarm_based.GTO import Matlab102GTO
from mealpy.evolutionary_based.ES import Simple_CMA_ES
from mealpy.math_based.GBO import OriginalGBO

from models.car import Car
from models.racetrack import RaceTrack
from models.f1_simulation import F1Simulation
from utils.visualization import F1SimVisualization

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
        f1_simulation.initialize_setting(x_decoded['list_tyre_setting_all_laps'],x_decoded['list_car_status_will_be_pit'],x_decoded['list_engine_setting_all_stopwatches'],x_decoded['list_brake_setting_all_stopwatches'])
        f1_simulation.race()
        # return [f1_simulation.score(),f1_simulation.get_count_pitstop(),f1_simulation.get_count_engine_set(),f1_simulation.get_count_brake_set(),100-f1_simulation.get_engine_reliability(),100-f1_simulation.get_brake_reliability(),100-f1_simulation.get_engine_fuel_percent(),f1_simulation.get_count_blank_stopwatch()]
        return [f1_simulation.score(),f1_simulation.get_penalty_score()]
    
my_bounds=[
    # ListStringVar list_tyre_setting_all_laps,
    MixedSetVar(valid_sets=(car.tyres.list_tyre_set_name,)*NUMBER_OF_LAPS,name='list_tyre_setting_all_laps'),
    BoolVar(n_vars=NUMBER_OF_LAPS-1,name='list_car_status_will_be_pit'),
    # ListStringVar list_engine_setting_all_stopwatches,
    MixedSetVar(valid_sets=(car.engine.list_engine_mode_name,)*(NUMBER_OF_LAPS*racetrack.num_stopwatch),name='list_engine_setting_all_stopwatches'),
    # ListStringVar list_brake_setting_all_stopwatches
    MixedSetVar(valid_sets=(car.brakes.list_brake_mode_name,)*(NUMBER_OF_LAPS*racetrack.num_stopwatch),name='list_brake_setting_all_stopwatches'),
]

# problem=F1OptimizationProblem(bound=my_bounds,minmax='min',car=car,racetrack=racetrack,number_of_laps=NUMBER_OF_LAPS, obj_weights=[1,1,1,1,1,1,1,1])
problem=F1OptimizationProblem(bound=my_bounds,minmax='min',car=car,racetrack=racetrack,number_of_laps=NUMBER_OF_LAPS, obj_weights=[1,1], name='F1OptimizationProblem')
model=HPSO_TVAC(epoch=2,pop_size=300)
model.solve(problem,mode='thread',n_workers=16)

print(f"Best agent: {model.g_best}")
print(f"Best solution: {model.g_best.solution}")
print(f"Best accuracy: {model.g_best.target.fitness}")
print(f"Best parameters: {model.problem.decode_solution(model.g_best.solution)}")

# re-create simulation, run it and visualize it
dict_decoded_solution=model.problem.decode_solution(model.g_best.solution)
f1_simulation=F1Simulation(car,racetrack,number_of_laps=66)
f1_simulation.initialize_setting(dict_decoded_solution['list_tyre_setting_all_laps'],dict_decoded_solution['list_car_status_will_be_pit'],dict_decoded_solution['list_engine_setting_all_stopwatches'],dict_decoded_solution['list_brake_setting_all_stopwatches'])
f1_simulation.race()
f1_viz=F1SimVisualization(f1_simulation)
f1_viz.plot_package("output/best")