from typing import Any
import numpy as np
import gymnasium as gym
from gymnasium import Env, spaces

from models.racetrack import RaceTrack
from models.car import Car, DICT_TYRE_SET, DICT_ENGINE_MODE, DICT_BRAKE_MODE

class F1Env(Env):
    def __init__(self) -> None:

        self.car=Car()
        self.racetrack=RaceTrack()
        self.number_of_laps=66
        self.num_stopwatch_all_laps=self.number_of_laps*self.racetrack.num_stopwatch

        # action_space, 4 aspects, tyres, pit next lap, engine mode, brake mode
        self.action_space=spaces.MultiDiscrete([len(DICT_TYRE_SET['list_tyre_set_name']),2,len(DICT_ENGINE_MODE['list_engine_mode_name']),len(DICT_BRAKE_MODE['list_brake_mode_name'])])
        # observational space, 13 parameters, current_tyre_setting, tyre_temperature, tyre_reliability, engine_temperature, engine_reliability, engine_fuel_level, brake_temperature, brake_reliability, car_in_pitlane, car_pitlane_mode, lap_idx, stopwatch_idx, num_watchstop_remain
        lb_observational_space=np.zeros((13,),dtype=np.float16)
        ub_observational_space=np.array([len(DICT_TYRE_SET['list_tyre_set_name']),np.finfo(np.float16).max,100,np.finfo(np.float16).max,100,np.finfo(np.float16).max,np.finfo(np.float16).max,100,1,1,self.number_of_laps,self.racetrack.num_stopwatch,self.number_of_laps*self.racetrack.num_stopwatch],dtype=np.float16)
        self.observation_space=spaces.Box(low=lb_observational_space,high=ub_observational_space,dtype=np.float16)

        # dynamic attributes and memory
        self.lap_idx=0
        self.stopwatch_idx=0
        self.lap_stopwatch_idx=0
        self.list_tyre_setting_all_laps=[None]*(self.number_of_laps*self.racetrack.num_stopwatch)
        self.list_car_status_will_be_pit=[None]*((self.number_of_laps)*self.racetrack.num_stopwatch)
        self.list_engine_setting_all_stopwatches=[None]*(self.number_of_laps*self.racetrack.num_stopwatch)
        self.list_brake_setting_all_stopwatches=[None]*(self.number_of_laps*self.racetrack.num_stopwatch)
        self.list_time_usage_all_stopwatches=[None]*(self.number_of_laps*self.racetrack.num_stopwatch)
        self.list_car_speed_all_stopwatches=[None]*(self.number_of_laps*self.racetrack.num_stopwatch)
        self.list_tyre_temperature_all_stopwatches=[None]*(self.number_of_laps*self.racetrack.num_stopwatch)
        self.list_tyre_reliability_all_stopwatches=[None]*(self.number_of_laps*self.racetrack.num_stopwatch)
        self.list_engine_temperature_all_stopwatches=[None]*(self.number_of_laps*self.racetrack.num_stopwatch)
        self.list_engine_horsepower_all_stopwatches=[None]*(self.number_of_laps*self.racetrack.num_stopwatch)
        self.list_engine_reliability_all_stopwatches=[None]*(self.number_of_laps*self.racetrack.num_stopwatch)
        self.list_engine_fuel_level_all_stopwatches=[None]*(self.number_of_laps*self.racetrack.num_stopwatch)
        self.list_brake_temperature_all_stopwatches=[None]*(self.number_of_laps*self.racetrack.num_stopwatch)
        self.list_brake_pressure_all_stopwatches=[None]*(self.number_of_laps*self.racetrack.num_stopwatch)
        self.list_brake_reliability_all_stopwatches=[None]*(self.number_of_laps*self.racetrack.num_stopwatch)
        self.car_in_pitlane=False
        self.dnf=False

        # other variable to check if available to race (step)
        self.state=None

    def reset(self, *, seed: int | None = None, options: dict[str, Any] | None = None) -> tuple[Any, dict[str, Any]]:
        # reset any status from car
        self.car.tyres.set_tyre_set(DICT_TYRE_SET['list_tyre_set_name'][0])
        self.car.tyres.reset_tyre_stat()
        self.car.engine.set_engine_mode(DICT_ENGINE_MODE['list_engine_mode_name'][0])
        self.car.engine.reset_engine_stat()
        self.car.engine.set_init_fuel_volume(100)
        self.car.brakes.set_brake_mode(DICT_BRAKE_MODE['list_brake_mode_name'][0])
        self.car.brakes.reset_brake_stat()
        self.car.set_car_pitlane_mode("OFF")

        # reset memory in env
        self.lap_idx=0
        self.stopwatch_idx=0
        self.lap_stopwatch_idx=0
        self.list_time_usage_all_stopwatches=[None]*(self.number_of_laps*self.racetrack.num_stopwatch)
        self.list_car_speed_all_stopwatches=[None]*(self.number_of_laps*self.racetrack.num_stopwatch)
        self.list_tyre_temperature_all_stopwatches=[None]*(self.number_of_laps*self.racetrack.num_stopwatch)
        self.list_tyre_reliability_all_stopwatches=[None]*(self.number_of_laps*self.racetrack.num_stopwatch)
        self.list_engine_temperature_all_stopwatches=[None]*(self.number_of_laps*self.racetrack.num_stopwatch)
        self.list_engine_horsepower_all_stopwatches=[None]*(self.number_of_laps*self.racetrack.num_stopwatch)
        self.list_engine_reliability_all_stopwatches=[None]*(self.number_of_laps*self.racetrack.num_stopwatch)
        self.list_engine_fuel_level_all_stopwatches=[None]*(self.number_of_laps*self.racetrack.num_stopwatch)
        self.list_brake_temperature_all_stopwatches=[None]*(self.number_of_laps*self.racetrack.num_stopwatch)
        self.list_brake_pressure_all_stopwatches=[None]*(self.number_of_laps*self.racetrack.num_stopwatch)
        self.list_brake_reliability_all_stopwatches=[None]*(self.number_of_laps*self.racetrack.num_stopwatch)
        self.car_in_pitlane=False
        self.dnf=False

        self.state=np.array([DICT_TYRE_SET['list_tyre_set_name'].index(self.car.tyres.tyre_set_name),self.car.tyres.tyre_temperature_celcius,self.car.tyres.tyre_reliability_percent,self.car.engine.engine_temperature_celcius,self.car.engine.engine_reliability_percent,self.car.engine.engine_fuel_volume_kg,self.car.brakes.brake_temperature_celcius,self.car.brakes.brake_reliability_percent,self.car_in_pitlane,0,self.lap_idx,self.stopwatch_idx,self.num_stopwatch_all_laps-self.lap_stopwatch_idx])

        return self.state, {}