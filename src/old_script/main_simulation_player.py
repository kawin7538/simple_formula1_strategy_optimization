import numpy as np
from models.car import Car
from models.racetrack import RaceTrack
from models.f1_simulation import F1Simulation
from utils.visualization import F1SimVisualization

car=Car()
racetrack=RaceTrack()
f1_simulation=F1Simulation(car,racetrack,number_of_laps=66)

# f1_simulation.initialize_setting(['Medium']*25+['Hard']*30+['Soft']*11,[False]*24+[True]+[False]*29+[True]+[False]*10,['Neutral']*(66*28),['Neutral']*(66*28))
# f1_simulation.initialize_setting(['Medium']*25+['Hard']*30+['Soft']*11,[False]*12+[True]+[False]*11+[True]+[False]*29+[True]+[False]*10,['Neutral']*(66*28),['Neutral']*(66*28))
# f1_simulation.race()
f1_simulation.initialize_setting(['Medium','Hard']*33,[True]*65,['Neutral']*(66*28),['Neutral',1,2]*(22*28))
f1_simulation.race()

f1_viz=F1SimVisualization(f1_simulation)
f1_viz.plot_package("output")
# f1_viz.plot_brake_setting_all_stopwatch('output/temp.png')