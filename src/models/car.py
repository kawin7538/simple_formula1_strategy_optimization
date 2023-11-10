from typing import Literal
import math

from models.engine import Engine
from models.tyres import Tyres
from models.brakes import Brakes

from config_data import DICT_ENGINE_MODE, DICT_TYRE_SET, DICT_BRAKE_MODE

class Car:
    def __init__(self) -> None:
        # static property
        self.base_weight_kg=700
        self.car_speed_km_hr_at_pitlane=80

        # car component property
        self.engine=Engine()
        self.tyres=Tyres()
        self.brakes=Brakes()

        # car component mode initialization
        self.engine.init_engine_mode(**DICT_ENGINE_MODE)
        self.tyres.init_tyre_set(**DICT_TYRE_SET)
        self.brakes.init_brake_mode(**DICT_BRAKE_MODE)

        # default setting at start
        self.set_engine_mode(self.engine.list_engine_mode_name[0])
        self.set_tyre_set(self.tyres.list_tyre_set_name[0])
        self.set_brake_mode(self.brakes.list_brake_mode_name[0])

        # dynamic property
        self.car_speed_km_hr=None
        self.car_pitlane_mode="OFF"

    def set_engine_mode(self, engine_mode_name:str|int):
        self.engine.set_engine_mode(engine_mode_name)

    def set_tyre_set(self, tyre_set_name:str|int):
        self.tyres.set_tyre_set(tyre_set_name)

    def set_brake_mode(self, brake_mode_name:str|int):
        self.brakes.set_brake_mode(brake_mode_name)

    def measure_car_speed(self):
        # car speed ~ (engine_rpm - diff_speed_from_tyres)*(1-diff_speed_ratio_from_brake)
        # engine_rpm ~ 1+ln(engine_horsepower)
        # diff_speed_ratio_from_brake ~ 1+ln(brake_pressure_psi)
        # or speed is constantly set to pitlane speed

        if self.car_pit_lane_mode=="OFF":
            # base speed from engine, equation were mocked up
            engine_rpm=1201.3*math.log(self.engine.engine_horsepower)+6021.7
            temp_car_speed_km_hr=(5e-7*engine_rpm+0.0167*engine_rpm-17.559)

            # speed decoration from tyre
            temp_car_speed_km_hr=temp_car_speed_km_hr-self.tyres.tyre_relative_speed_loss_km_hr

            # speed decoration from brake pressure, equation were mocked up
            diff_speed_ratio_from_brake=0.5837*math.log(self.brakes.brake_pressure_psi)-4.3773
            self.car_speed_km_hr=temp_car_speed_km_hr*(1-diff_speed_ratio_from_brake)

        else:
            self.car_speed_km_hr=self.car_speed_km_hr_at_pitlane

    def set_car_pitlane_mode(self, car_pitlane_mode:Literal["OFF","ON"]):
        self.car_pitlane_mode=car_pitlane_mode

    def is_drivable(self):
        return self.engine.is_usable() and self.brakes.is_usable()