import numpy as np
from mealpy import Problem, FloatVar, IntegerVar, BoolVar
from mealpy.swarm_based.GWO import GWO_WOA

class CustomProblem(Problem):
    def __init__(self, bound=None, minmax='min', **kwargs):
        super().__init__(bound,minmax,**kwargs)

    def obj_func(self,x):
        x_decoded=self.decode_solution(x)
        return np.sum(x_decoded['float_var']**2)+np.sum(x_decoded['int_var']**2)+np.sum(x_decoded['boolean_var']**2)
    
my_bounds=[
    FloatVar(lb=(-10,)*50,ub=(100,)*50,name='float_var'),
    IntegerVar(lb=(-5,)*50,ub=(-1,)*50,name='int_var'),
    BoolVar(n_vars=50,name='boolean_var')
]

problem=CustomProblem(bound=my_bounds,minmax='min')
model=GWO_WOA(epoch=2000,pop_size=500)
model.solve(problem)