from collections import deque

MEMORY_SIZE=3

class Engine:
    def __init__(self) -> None:
        
        # static property
        self.list_engine_mode_name=[]
        self.list_engine_mode_base_reliability_percent_loss_per_lap=[]
        self.list_engine_mode_base_maximum_horsepower=[]
        self.list_engine_mode_fuel_volume_consuming_kg_per_lap=[]
        self.list_engine_mode_temperature_celcius=[]

        # dynamic property from steering wheel
        self.engine_mode_name=''
        self.engine_mode_base_reliability_percent_loss_per_lap=None
        self.engine_mode_base_maximum_horsepower=None
        self.engine_mode_fuel_volume_consuming_kg_per_lap=None
        self.engine_mode_temperature_celcius=None

        # dynamic property from sensors
        self.engine_reliability_percent=100
        self.engine_horsepower=0
        self.engine_fuel_volume_kg=0
        self.engine_temperature_celcius=50

        # dynamic memory
        self.engine_temperature_memory_celcius=deque(maxlen=MEMORY_SIZE)

    def config_engine_mode(self, list_engine_mode_name:list[str|int], list_engine_mode_base_reliability_percent_loss_per_lap:list[int|float], list_engine_mode_base_maximum_horsepower:list[int|float], list_engine_mode_fuel_volume_consuming_kg_per_lap:list[int|float], list_engine_mode_temperature_celcius:list[int|float]):
        assert len(set([len(list_engine_mode_name), len(list_engine_mode_base_reliability_percent_loss_per_lap), len(list_engine_mode_base_maximum_horsepower), len(list_engine_mode_fuel_volume_consuming_kg_per_lap), len(list_engine_mode_temperature_celcius)]))==1

    def set_engine_mode(self,engine_mode_name:int|str):
        assert engine_mode_name in self.list_engine_mode_name

        engine_mode_idx=self.list_engine_mode_name.index(engine_mode_name)
        self.engine_mode_name=self.list_engine_mode_name[engine_mode_idx]
        self.engine_mode_base_reliability_percent_loss_per_lap=self.list_engine_mode_base_reliability_percent_loss_per_lap[engine_mode_idx]
        self.engine_mode_base_maximum_horsepower=self.list_engine_mode_base_maximum_horsepower[engine_mode_idx]
        self.engine_mode_fuel_volume_consuming_kg_per_lap=self.list_engine_mode_fuel_volume_consuming_kg_per_lap[engine_mode_idx]
        self.engine_mode_temperature_celcius=self.list_engine_mode_temperature_celcius[engine_mode_idx]

    def set_init_fuel_volume(self,fuel_volume_kg:int|float):
        assert fuel_volume_kg>0

        self.engine_fuel_volume_kg=fuel_volume_kg

    def decrease_fuel_volume(self, diff_fuel_volume_kg:int|float):
        assert diff_fuel_volume_kg>0

        self.engine_fuel_volume_kg=max(0,self.engine_fuel_volume_kg-diff_fuel_volume_kg)

    def decrease_engine_reliability(self, diff_engine_reliability_percent:int|float):
        assert diff_engine_reliability_percent>=0

        self.engine_reliability_percent=max(0,self.engine_reliability_percent-diff_engine_reliability_percent)

    def measure_engine_temperature(self):
        self.engine_temperature_memory_celcius.append(self.engine_temperature_celcius)
        self.engine_temperature_celcius=(sum(self.engine_temperature_memory_celcius)+self.engine_mode_temperature_celcius)/(MEMORY_SIZE+1)

    def is_usable(self):
        return self.engine_reliability_percent>0 and self.engine_fuel_volume_kg>0