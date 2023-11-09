from collections import deque

MEMORY_SIZE=10

class Brakes:
    def __init__(self) -> None:
        
        # static property
        self.list_brake_mode_name=[]
        self.list_brake_mode_base_brake_pressure_psi=[]
        self.list_brake_mode_base_brake_temperature_celcius=[]
        self.list_brake_mode_base_reliability_percent_loss_per_lap=[]

        # dynamic property from steering wheel
        self.brake_mode_name=''
        self.brake_mode_base_brake_pressure_psi=None
        self.brake_mode_base_brake_temperature_celcius=None
        self.brake_mode_base_reliability_percent_loss_per_lap=None

        # dynamic property from sensors
        self.brake_pressure_psi=500
        self.brake_temperature_celcius=40
        self.brake_reliability_percent=100

        # dynamic memory
        self.brake_temperature_memory_celcius=deque(maxlen=MEMORY_SIZE)

    def init_brake_mode(self, list_brake_mode_name:list[str|int], list_brake_mode_base_brake_pressure_psi:list[int|float], list_brake_mode_base_brake_temperature_celcius:list[int|float], list_brake_mode_base_reliability_percent_loss_per_lap:list[int|float]):
        assert len(set([len(list_brake_mode_name), len(list_brake_mode_base_brake_pressure_psi), len(list_brake_mode_base_brake_temperature_celcius), len(list_brake_mode_base_reliability_percent_loss_per_lap)]))==1

        self.list_brake_mode_name=list_brake_mode_name
        self.list_brake_mode_base_brake_pressure_psi=list_brake_mode_base_brake_pressure_psi
        self.list_brake_mode_base_brake_temperature_celcius=list_brake_mode_base_brake_temperature_celcius
        self.list_brake_mode_base_reliability_percent_loss_per_lap=list_brake_mode_base_reliability_percent_loss_per_lap

    def set_brake_mode(self, brake_mode_name:int|str):
        assert brake_mode_name in self.list_brake_mode_name

        brake_mode_idx=self.list_brake_mode_name.index(brake_mode_name)
        self.brake_mode_name=self.list_brake_mode_name[brake_mode_idx]
        self.brake_mode_base_brake_pressure_psi=self.list_brake_mode_base_brake_pressure_psi[brake_mode_idx]
        self.brake_mode_base_brake_temperature_celcius=self.list_brake_mode_base_brake_temperature_celcius[brake_mode_idx]
        self.brake_mode_base_reliability_percent_loss_per_lap=self.list_brake_mode_base_reliability_percent_loss_per_lap[brake_mode_idx]

    def decrease_brake_reliability(self, diff_brake_reliability_percent:int|float):
        assert diff_brake_reliability_percent>=0

        self.brake_reliability_percent=max(0,self.brake_reliability_percent-diff_brake_reliability_percent)

    def measure_brake_pressure(self):
        # calculate brake pressure based on based setting, reliability, and temperature
        self.brake_pressure_psi=max(0,self.brake_mode_base_brake_pressure_psi-0.6*(100-self.brake_reliability_percent)*self.brake_mode_base_brake_pressure_psi-1/75*self.brake_temperature_celcius)

    def measure_brake_temperature(self):
        self.brake_temperature_memory_celcius.append(self.brake_temperature_celcius)
        self.brake_temperature_celcius=(sum(self.brake_temperature_memory_celcius)+self.brake_mode_base_brake_temperature_celcius)/(len(self.brake_temperature_memory_celcius)+1)

    def is_usable(self):
        return self.brake_reliability_percent>0