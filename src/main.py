from models.car import Car
from models.racetrack import RaceTrack
from models.f1_simulation import F1Simulation

car=Car()
racetrack=RaceTrack()
f1_simulation=F1Simulation(car,racetrack,number_of_laps=66)

f1_simulation.initialize_setting(['Medium']*25+['Hard']*30+['Soft']*11,['Neutral']*(66*28),['Neutral']*(66*28))
f1_simulation.race()