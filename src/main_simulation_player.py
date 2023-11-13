from models.car import Car
from models.racetrack import RaceTrack
from models.f1_simulation import F1Simulation
from utils.visualization import F1SimVisualization

car=Car()
racetrack=RaceTrack()
f1_simulation=F1Simulation(car,racetrack,number_of_laps=66)

# f1_simulation.initialize_setting(['Medium']*25+['Hard']*30+['Soft']*11,[False]*24+[True]+[False]*29+[True]+[False]*10,['Neutral']*(66*28),['Neutral']*(66*28))
f1_simulation.initialize_setting(['Medium']*25+['Hard']*30+['Soft']*11,[False]*12+[True]+[False]*11+[True]+[False]*29+[True]+[False]*10,['Neutral']*(66*28),['Neutral']*(66*28))
f1_simulation.race()

f1_viz=F1SimVisualization(f1_simulation)
f1_viz.plot_tyre_sequence("output/tyre_sequence.png")
f1_viz.plot_car_speed("output/car_speed.png")
f1_viz.plot_laptime_all_stopwatch("output/laptime_all_stopwatch.png")
f1_viz.plot_engine_horsepower_all_stopwatch("output/engine_horsepower_all_stopwatch.png")
f1_viz.plot_engine_reliability_all_stopwatch("output/engine_reliability_all_stopwatch.png")
f1_viz.plot_fuel_level_all_stopwatch("output/engine_fuel_level_all_stopwatch.png")
f1_viz.plot_engine_temperature_all_stopwatch("output/engine_temperature_all_stopwatch.png")
f1_viz.plot_brake_pressure_all_stopwatch("output/brake_pressure_all_stopwatch.png")
f1_viz.plot_brake_reliability_all_stopwatch("output/brake_reliability_all_stopwatch.png")
f1_viz.plot_brake_temperature_all_stopwatch("output/brake_temperature_all_stopwatch.png")
f1_viz.plot_tyre_reliability_all_stopwatch("output/tyre_reliability_all_stopwatch.png")
f1_viz.plot_tyre_temperature_all_stopwatch("output/tyre_temperature_all_stopwatch.png")