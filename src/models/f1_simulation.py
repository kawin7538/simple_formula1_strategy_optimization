from typing import Literal

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

    def race(self):
        assert None not in self.list_tyre_setting_all_laps
        assert None not in self.list_engine_setting_all_stopwatches
        assert None not in self.list_brake_setting_all_stopwatches

        self.car.set_tyre_set(self.list_tyre_setting_all_laps[0])
        self.car.tyres.reset_tyre_stat()
        
        for lap_idx in range(self.number_of_laps):
            for stopwatch_idx in range(self.racetrack.num_stopwatch):
                if not self.car.is_drivable():
                    self.dnf=True
                    return;
                # overall steps for each stopwatch section
                # set engine mode
                # set brake mode
                # measure temperature of engine
                # measure temperature of brake
                # measure temperature of tyres
                # measure car engine horsepower
                # measure car brake pressure
                # measure car tyre speed loss
                # measure car speed due to pit lane condition
                # measure time usage
                # decrease reliability of engine
                # decrease reliability of brake
                # decrease reliability of tyres
                # car moved to next stopwatch, repeat these steps until chequered flag or dnf