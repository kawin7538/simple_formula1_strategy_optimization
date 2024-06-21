from typing import Any, SupportsFloat
from itertools import product
import numpy as np
import gymnasium as gym
from gymnasium import Env, spaces

from xuance.environment import RawEnvironment

from models.racetrack import RaceTrack
from models.car import Car, DICT_TYRE_SET, DICT_ENGINE_MODE, DICT_BRAKE_MODE

LIST_ACTIONS=list(product(range(len(DICT_TYRE_SET['list_tyre_set_name'])),[0,1],range(len(DICT_ENGINE_MODE['list_engine_mode_name'])),range(len(DICT_BRAKE_MODE['list_brake_mode_name']))))

class XuanceF1Env(RawEnvironment):
    def __init__(self, env_config) -> None:

        self.car=Car()
        self.racetrack=RaceTrack()
        self.number_of_laps=66
        self.num_stopwatch_all_laps=self.number_of_laps*self.racetrack.num_stopwatch
        self.max_episode_steps=self.num_stopwatch_all_laps

        # action_space, 4 aspects, tyres next lap, pit next lap, engine mode, brake mode
        # self.action_space=spaces.MultiDiscrete([len(DICT_TYRE_SET['list_tyre_set_name']),2,len(DICT_ENGINE_MODE['list_engine_mode_name']),len(DICT_BRAKE_MODE['list_brake_mode_name'])])
        self.action_space=spaces.Discrete(len(DICT_TYRE_SET['list_tyre_set_name'])*2*len(DICT_ENGINE_MODE['list_engine_mode_name'])*len(DICT_BRAKE_MODE['list_brake_mode_name']))
        # observational space, 12 parameters, current_tyre_setting, tyre_temperature, tyre_reliability, engine_temperature, engine_reliability, engine_fuel_level, brake_temperature, brake_reliability, car_in_pitlane, lap_idx, stopwatch_idx, num_watchstop_remain
        lb_observational_space=np.zeros((12,),dtype=np.float32)
        ub_observational_space=np.array([len(DICT_TYRE_SET['list_tyre_set_name']),np.finfo(np.float32).max,100,np.finfo(np.float32).max,100,np.finfo(np.float32).max,np.finfo(np.float32).max,100,1,self.number_of_laps,self.racetrack.num_stopwatch,self.number_of_laps*self.racetrack.num_stopwatch],dtype=np.float32)
        self.observation_space=spaces.Box(low=lb_observational_space,high=ub_observational_space,dtype=np.float32)

        # dynamic attributes and memory
        self.lap_idx=0
        self.stopwatch_idx=0
        self.lap_stopwatch_idx=0
        self.list_tyre_setting_all_laps=[None]*self.number_of_laps
        self.list_car_status_will_be_pit=[None]*(self.number_of_laps-1)
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
        self.list_tyre_setting_all_laps=[None]*self.number_of_laps
        self.list_car_status_will_be_pit=[None]*(self.number_of_laps-1)
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

        self.state=np.array([DICT_TYRE_SET['list_tyre_set_name'].index(self.car.tyres.tyre_set_name),self.car.tyres.tyre_temperature_celcius,self.car.tyres.tyre_reliability_percent,self.car.engine.engine_temperature_celcius,self.car.engine.engine_reliability_percent,self.car.engine.engine_fuel_volume_kg,self.car.brakes.brake_temperature_celcius,self.car.brakes.brake_reliability_percent,self.car_in_pitlane,self.lap_idx,self.stopwatch_idx,self.num_stopwatch_all_laps-self.lap_stopwatch_idx])

        return self.state, {}
    
    def step(self, action: Any) -> tuple[Any, SupportsFloat, bool, bool, dict[str, Any]]:
        assert self.action_space.contains(
            action
        ), f"{action!r} ({type(action)}) invalid"
        assert self.state is not None, "Call reset before using step method."

        # tyre_set_idx, pit_next_lap, engine_mode_idx, brake_mode_idx = action
        tyre_set_idx, pit_next_lap, engine_mode_idx, brake_mode_idx = LIST_ACTIONS[action]

        # set engine_mode
        self.car.engine.set_engine_mode(DICT_ENGINE_MODE['list_engine_mode_name'][engine_mode_idx])
        self.list_engine_setting_all_stopwatches[self.racetrack.num_stopwatch*self.lap_idx+self.stopwatch_idx]=self.car.engine.engine_mode_name
        # set brake_mode
        self.car.brakes.set_brake_mode(DICT_BRAKE_MODE['list_brake_mode_name'][brake_mode_idx])
        self.list_brake_setting_all_stopwatches[self.racetrack.num_stopwatch*self.lap_idx+self.stopwatch_idx]=self.car.brakes.brake_mode_name
        # measure temperature of engine
        self.car.engine.measure_engine_temperature()
        self.list_engine_temperature_all_stopwatches[self.racetrack.num_stopwatch*self.lap_idx+self.stopwatch_idx]=self.car.engine.engine_temperature_celcius
        # measure temperature of brake
        self.car.brakes.measure_brake_temperature()
        self.list_brake_temperature_all_stopwatches[self.racetrack.num_stopwatch*self.lap_idx+self.stopwatch_idx]=self.car.brakes.brake_temperature_celcius
        # measure temperature of tyres
        self.car.tyres.measure_tyre_temperature(self.racetrack.racetrack_temperature_celcius,self.car.brakes.brake_temperature_celcius)
        self.list_tyre_temperature_all_stopwatches[self.racetrack.num_stopwatch*self.lap_idx+self.stopwatch_idx]=self.car.tyres.tyre_temperature_celcius
        # measure car engine horsepower
        self.car.engine.measure_engine_horsepower()
        self.list_engine_horsepower_all_stopwatches[self.racetrack.num_stopwatch*self.lap_idx+self.stopwatch_idx]=self.car.engine.engine_horsepower
        # measure car brake pressure
        self.car.brakes.measure_brake_pressure()
        self.list_brake_pressure_all_stopwatches[self.racetrack.num_stopwatch*self.lap_idx+self.stopwatch_idx]=self.car.brakes.brake_pressure_psi
        # measure car tyre speed loss
        self.car.tyres.calculate_tyre_relative_speed_loss()
        # check condition before retire or something
        if not self.car.is_drivable():
            self.dnf=True
            terminated=True
            # reward=-(1e9+sum([1 for val in self.list_time_usage_all_stopwatches if val==None]))
            reward=-sum([1e6 for val in self.list_time_usage_all_stopwatches if val==None])
            self.state=np.array([DICT_TYRE_SET['list_tyre_set_name'].index(self.car.tyres.tyre_set_name),self.car.tyres.tyre_temperature_celcius,self.car.tyres.tyre_reliability_percent,self.car.engine.engine_temperature_celcius,self.car.engine.engine_reliability_percent,self.car.engine.engine_fuel_volume_kg,self.car.brakes.brake_temperature_celcius,self.car.brakes.brake_reliability_percent,self.car_in_pitlane,self.lap_idx,self.stopwatch_idx,self.num_stopwatch_all_laps-self.lap_stopwatch_idx])
            return np.array(self.state, dtype=np.float32), reward, terminated, False, {}
        # firstly init first stint for lap 0 and stopwatch 0
        if self.lap_idx==0 and self.stopwatch_idx==0:
            self.car.tyres.set_tyre_set(DICT_TYRE_SET['list_tyre_set_name'][tyre_set_idx])
            self.car.tyres.reset_tyre_stat()
        # check goto pitstop condition on current lap idx
        if self.lap_idx<self.number_of_laps-1:
            if pit_next_lap==True and self.stopwatch_idx==self.racetrack.start_end_pitlane_stopwatch[0] and self.car_in_pitlane==False:
                self.car_in_pitlane=True
                self.list_car_status_will_be_pit[self.lap_idx]=True
                self.car.set_car_pitlane_mode("ON")
            elif pit_next_lap==False and self.stopwatch_idx==self.racetrack.start_end_pitlane_stopwatch[0] and self.car_in_pitlane==False:
                self.list_car_status_will_be_pit[self.lap_idx]=False
        if self.car_in_pitlane==True and self.stopwatch_idx==0:
            self.car.tyres.set_tyre_set(DICT_TYRE_SET['list_tyre_set_name'][tyre_set_idx])
            self.car.tyres.reset_tyre_stat()
        if self.car_in_pitlane==True and self.stopwatch_idx==self.racetrack.start_end_pitlane_stopwatch[1]:
            self.car_in_pitlane=False
            self.car.set_car_pitlane_mode("OFF")
        # check if stopwatch_idx==0, then memorized current tyre set
        if self.stopwatch_idx==0:
            self.list_tyre_setting_all_laps[self.lap_idx]=self.car.tyres.tyre_set_name
        # measure car speed due to pit lane condition
        self.car.measure_car_speed()
        self.list_car_speed_all_stopwatches[self.racetrack.num_stopwatch*self.lap_idx+self.stopwatch_idx]=self.car.car_speed_km_hr
        # judge all driving that contains speed==0 as DNF
        if self.car.car_speed_km_hr<=0:
            self.dnf=True
            terminated=True
            # reward=-(1e9+sum([1 for val in self.list_time_usage_all_stopwatches if val==None]))
            reward=-sum([1e6 for val in self.list_time_usage_all_stopwatches if val==None])
            self.state=np.array([DICT_TYRE_SET['list_tyre_set_name'].index(self.car.tyres.tyre_set_name),self.car.tyres.tyre_temperature_celcius,self.car.tyres.tyre_reliability_percent,self.car.engine.engine_temperature_celcius,self.car.engine.engine_reliability_percent,self.car.engine.engine_fuel_volume_kg,self.car.brakes.brake_temperature_celcius,self.car.brakes.brake_reliability_percent,self.car_in_pitlane,self.lap_idx,self.stopwatch_idx,self.num_stopwatch_all_laps-self.lap_stopwatch_idx])
            return np.array(self.state, dtype=np.float32), reward, terminated, False, {}
        # measure time usage
        self.list_time_usage_all_stopwatches[self.racetrack.num_stopwatch*self.lap_idx+self.stopwatch_idx]=(self.racetrack.distance_km/self.racetrack.num_stopwatch)/self.car.car_speed_km_hr*3600
        # if tyre reliability got 0%, plus additional time usage on that stopwatch and recalculate for speed
        if self.car.tyres.tyre_reliability_percent==0:
            self.list_time_usage_all_stopwatches[self.racetrack.num_stopwatch*self.lap_idx+self.stopwatch_idx]+=(self.car.tyres.tyre_set_laptime_loss_per_lap_zero_reliability_seconds/self.racetrack.num_stopwatch)
            self.car.car_speed_km_hr=(self.racetrack.distance_km/self.racetrack.num_stopwatch)/(self.list_time_usage_all_stopwatches[self.racetrack.num_stopwatch*self.lap_idx+self.stopwatch_idx]/3600)
            self.list_car_speed_all_stopwatches[self.racetrack.num_stopwatch*self.lap_idx+self.stopwatch_idx]=self.car.car_speed_km_hr
        # plus laptime for pitting
        if self.car_in_pitlane==True and self.stopwatch_idx==0:
            self.list_time_usage_all_stopwatches[self.racetrack.num_stopwatch*self.lap_idx+self.stopwatch_idx]+=2
        # decrease reliability of engine
        self.car.engine.decrease_engine_reliability(self.car.engine.engine_mode_base_reliability_percent_loss_per_lap/self.racetrack.num_stopwatch)
        self.list_engine_reliability_all_stopwatches[self.racetrack.num_stopwatch*self.lap_idx+self.stopwatch_idx]=self.car.engine.engine_reliability_percent
        # decrease reliability of brake
        self.car.brakes.decrease_brake_reliability(self.car.brakes.brake_mode_base_reliability_percent_loss_per_lap/self.racetrack.num_stopwatch)
        self.list_brake_reliability_all_stopwatches[self.racetrack.num_stopwatch*self.lap_idx+self.stopwatch_idx]=self.car.brakes.brake_reliability_percent
        # decrease reliability of tyres
        self.car.tyres.decrease_tyre_reliability(self.car.tyres.tyre_set_base_reliability_percent_loss_per_lap/self.racetrack.num_stopwatch)
        self.list_tyre_reliability_all_stopwatches[self.racetrack.num_stopwatch*self.lap_idx+self.stopwatch_idx]=self.car.tyres.tyre_reliability_percent
        # decrease engine fuel
        self.car.engine.decrease_fuel_volume(self.car.engine.engine_mode_fuel_volume_consuming_kg_per_lap/self.racetrack.num_stopwatch)
        self.list_engine_fuel_level_all_stopwatches[self.racetrack.num_stopwatch*self.lap_idx+self.stopwatch_idx]=self.car.engine.engine_fuel_volume_kg

        # update rewards
        terminated=False
        is_done=False
        reward=-self.list_time_usage_all_stopwatches[self.racetrack.num_stopwatch*self.lap_idx+self.stopwatch_idx]
        dict_info=dict()

        # update states
        self.stopwatch_idx+=1
        if self.stopwatch_idx>=self.racetrack.num_stopwatch:
            self.lap_idx+=1
            self.stopwatch_idx=0
        self.lap_stopwatch_idx=self.racetrack.num_stopwatch*self.lap_idx+self.stopwatch_idx
        self.state=np.array([DICT_TYRE_SET['list_tyre_set_name'].index(self.car.tyres.tyre_set_name),self.car.tyres.tyre_temperature_celcius,self.car.tyres.tyre_reliability_percent,self.car.engine.engine_temperature_celcius,self.car.engine.engine_reliability_percent,self.car.engine.engine_fuel_volume_kg,self.car.brakes.brake_temperature_celcius,self.car.brakes.brake_reliability_percent,self.car_in_pitlane,self.lap_idx,self.stopwatch_idx,self.num_stopwatch_all_laps-self.lap_stopwatch_idx])

        # if self.num_stopwatch_all_laps-self.lap_stopwatch_idx<=0:
        if not None in self.list_time_usage_all_stopwatches:
            if len(set(self.list_tyre_setting_all_laps))<=1:
                terminated=True
                self.dnf=True
                reward=-5e5
            else:
                is_done=True
                dict_info['overall_time']=sum(self.list_time_usage_all_stopwatches)
                # reward=(-sum(self.list_time_usage_all_stopwatches)/50-self.car.engine.engine_reliability_percent-self.car.brakes.brake_reliability_percent)
        else:
            # reward=0
            # if self.car.tyres.tyre_reliability_percent==0:
            #     reward-=1
            # if pit_next_lap==True:
            #     reward-=1
            # else:
            #     reward=0
            pass;

        return np.array(self.state, dtype=np.float32), reward, terminated, is_done, dict_info
    
    def render(self, *args, **kwargs):
        return super().render(*args, **kwargs)
    
    def close(self):
        return super().close()