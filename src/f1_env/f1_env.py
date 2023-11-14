import gymnasium as gym
from gymnasium import Env, spaces

from models.car import Car, DICT_TYRE_SET, DICT_ENGINE_MODE, DICT_BRAKE_MODE

class F1Env(Env):
    def __init__(self) -> None:
        # action_space, 4 aspects, tyres, pit next lap, engine mode, brake mode
        self.action_space=spaces.MultiDiscrete([len(DICT_TYRE_SET['list_tyre_set_name']),2,len(DICT_ENGINE_MODE['list_engine_mode_name']),len(DICT_BRAKE_MODE['list_brake_mode_name'])])