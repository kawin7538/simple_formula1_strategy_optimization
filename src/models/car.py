from models.engine import Engine
from models.tyres import Tyres
from models.brakes import Brakes

from config_data import DICT_ENGINE_MODE, DICT_TYRE_SET, DICT_BRAKE_MODE

class Car:
    def __init__(self) -> None:
        self.base_weight_kg=700

        self.engine=Engine()
        self.tyres=Tyres()
        self.brakes=Brakes()

        self.engine.init_engine_mode(**DICT_ENGINE_MODE)