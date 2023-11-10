from typing import Literal
from datetime import timedelta

from models.car import Car
from models.racetrack import RaceTrack

class F1Simulation:
    def __init__(self, car:Car, racetrack:RaceTrack, number_of_laps:int) -> None:
        assert number_of_laps>0

        # static property
        self.car=car
        self.racetrack=racetrack
        self.number_of_laps=number_of_laps

        self.list_available_tyre_settings=self.car.tyres.list_tyre_set_name

        # dynamic property which will be set from user
        self.list_tyre_setting_all_laps=[None]*number_of_laps
        self.list_engine_setting_all_stopwatches=[None]*(number_of_laps*self.racetrack.num_stopwatch)
        self.list_brake_setting_all_stopwatches=[None]*(number_of_laps*self.racetrack.num_stopwatch)

        # dynamic memory simulated from user's input
        self.list_time_usage_all_stopwatches=[None]*(number_of_laps*self.racetrack.num_stopwatch)
        self.list_car_speed_all_stopwatches=[None]*(number_of_laps*self.racetrack.num_stopwatch)
        self.list_car_status_will_be_pit=[False]*(number_of_laps-1)
        self.car_in_pitlane=False
        self.dnf=False

    def initialize_setting(self, list_tyre_setting_all_laps:list, list_engine_setting_all_stopwatches:list, list_brake_setting_all_stopwatches:list):
        assert len(self.list_tyre_setting_all_laps)==len(list_tyre_setting_all_laps)
        assert len(self.list_engine_setting_all_stopwatches)==len(list_engine_setting_all_stopwatches)
        assert len(self.list_brake_setting_all_stopwatches)==len(list_brake_setting_all_stopwatches)
        assert None not in list_tyre_setting_all_laps
        assert None not in list_engine_setting_all_stopwatches
        assert None not in list_brake_setting_all_stopwatches

        self.list_tyre_setting_all_laps=list_tyre_setting_all_laps
        self.list_engine_setting_all_stopwatches=list_engine_setting_all_stopwatches
        self.list_brake_setting_all_stopwatches=list_brake_setting_all_stopwatches

        # check when go to pit
        for i in range(self.number_of_laps-1):
            if self.list_tyre_setting_all_laps[i]!=self.list_tyre_setting_all_laps[i+1]:
                self.list_car_status_will_be_pit[i]=True

    def race(self, verbose=False):
        assert None not in self.list_tyre_setting_all_laps
        assert None not in self.list_engine_setting_all_stopwatches
        assert None not in self.list_brake_setting_all_stopwatches

        self.car.set_tyre_set(self.list_tyre_setting_all_laps[0])
        self.car.tyres.reset_tyre_stat()
        self.car.engine.set_init_fuel_volume(100)
        
        for lap_idx in range(self.number_of_laps):
            for stopwatch_idx in range(self.racetrack.num_stopwatch):
                # overall steps for each stopwatch section
                # set engine mode
                self.car.set_engine_mode(self.list_engine_setting_all_stopwatches[self.racetrack.num_stopwatch*lap_idx+stopwatch_idx])
                # set brake mode
                self.car.set_brake_mode(self.list_brake_setting_all_stopwatches[self.racetrack.num_stopwatch*lap_idx+stopwatch_idx])
                # measure temperature of engine
                self.car.engine.measure_engine_temperature()
                # measure temperature of brake
                self.car.brakes.measure_brake_temperature()
                # measure temperature of tyres
                self.car.tyres.measure_tyre_temperature(self.racetrack.racetrack_temperature_celcius,self.car.brakes.brake_temperature_celcius)
                # measure car engine horsepower
                self.car.engine.measure_engine_horsepower()
                # measure car brake pressure
                self.car.brakes.measure_brake_pressure()
                # measure car tyre speed loss
                self.car.tyres.calculate_tyre_relative_speed_loss()
                # check condition before retire or something
                if not self.car.is_drivable():
                    self.dnf=True
                    print("DNF")
                    print(lap_idx)
                    return;
                # measure car speed due to pit lane condition
                self.car.measure_car_speed()
                if self.car.tyres.tyre_reliability_percent==0:
                    self.car.car_speed_km_hr+=(self.car.tyres.tyre_set_laptime_loss_per_lap_zero_reliability_seconds/self.racetrack.num_stopwatch)
                self.list_car_speed_all_stopwatches[self.racetrack.num_stopwatch*lap_idx+stopwatch_idx]=self.car.car_speed_km_hr
                # measure time usage
                self.list_time_usage_all_stopwatches[self.racetrack.num_stopwatch*lap_idx+stopwatch_idx]=(self.racetrack.distance_km/self.racetrack.num_stopwatch)/self.car.car_speed_km_hr*3600
                # decrease reliability of engine
                self.car.engine.decrease_engine_reliability(self.car.engine.engine_mode_base_reliability_percent_loss_per_lap/self.racetrack.num_stopwatch)
                # decrease reliability of brake
                self.car.brakes.decrease_brake_reliability(self.car.brakes.brake_mode_base_reliability_percent_loss_per_lap/self.racetrack.num_stopwatch)
                # decrease reliability of tyres
                self.car.tyres.decrease_tyre_reliability(self.car.tyres.tyre_set_base_reliability_percent_loss_per_lap/self.racetrack.num_stopwatch)
                # decrease engine fuel
                self.car.engine.decrease_fuel_volume(self.car.engine.engine_mode_fuel_volume_consuming_kg_per_lap/self.racetrack.num_stopwatch)
                # car moved to next stopwatch, repeat these steps until chequered flag or dnf