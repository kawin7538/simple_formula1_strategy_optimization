import math

from models.engine import Engine
from models.tyres import Tyres
from models.brakes import Brakes

from config_data import DICT_ENGINE_MODE, DICT_TYRE_SET, DICT_BRAKE_MODE

class Car:
    def __init__(self) -> None:
        # static property
        self.base_weight_kg=700

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

    def set_engine_mode(self, engine_mode_name:str|int):
        self.engine.set_engine_mode(engine_mode_name)

    def set_tyre_set(self, tyre_set_name:str|int):
        self.tyres.set_tyre_set(tyre_set_name)

    def set_brake_mode(self, brake_mode_name:str|int):
        self.brakes.set_brake_mode(brake_mode_name)

    def measure_car_speed(self):
        # car speed ~ engine_horsepower
        engine_rpm=1201.3*math.log(self.engine.engine_horsepower)+6021.7
        self.car_speed_km_hr=(5e-7*engine_rpm+0.0167*engine_rpm-17.559)
        pass;