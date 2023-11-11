from collections import deque

MEMORY_SIZE=28*5

class Tyres:
    def __init__(self) -> None:

        # static property
        self.list_tyre_set_name=[]
        self.list_tyre_set_base_reliability_percent_loss_per_lap=[]
        self.list_tyre_set_optimal_temperature_celcius=[]
        # self.list_tyre_set_relative_laptime_loss_per_lap_seconds=[]
        self.list_tyre_set_relative_speed_loss_km_hr=[]
        self.tyre_set_laptime_loss_per_lap_zero_reliability_seconds=60.

        # dynamic property from pit lane
        self.tyre_set_name=''
        self.tyre_set_base_reliability_percent_loss_per_lap=None
        self.tyre_set_optimal_temperature_celcius=None
        # self.tyre_set_relative_laptime_loss_per_lap_seconds=None
        self.tyre_set_relative_speed_loss_km_hr=None

        # dynamic property from sensors
        self.tyre_reliability_percent=100
        self.tyre_temperature_celcius=100
        self.tyre_relative_speed_loss_km_hr=0

        # dynamic memory
        self.tyre_temperature_memory_celcius=deque(maxlen=MEMORY_SIZE)

    def init_tyre_set(self, list_tyre_set_name:list[str|int], list_tyre_set_base_reliability_percent_loss_per_lap:list[int|float], list_tyre_set_optimal_temperature_celcius:list[int|float], list_tyre_set_relative_speed_loss_km_hr:list[int|float]):
        assert len(set([len(list_tyre_set_name), len(list_tyre_set_base_reliability_percent_loss_per_lap), len(list_tyre_set_optimal_temperature_celcius), len(list_tyre_set_relative_speed_loss_km_hr)]))==1

        self.list_tyre_set_name=list_tyre_set_name
        self.list_tyre_set_base_reliability_percent_loss_per_lap=list_tyre_set_base_reliability_percent_loss_per_lap
        self.list_tyre_set_optimal_temperature_celcius=list_tyre_set_optimal_temperature_celcius
        self.list_tyre_set_relative_speed_loss_km_hr=list_tyre_set_relative_speed_loss_km_hr

    def set_tyre_set(self, tyre_set_name:str|int):
        assert tyre_set_name in self.list_tyre_set_name

        tyre_set_idx=self.list_tyre_set_name.index(tyre_set_name)
        self.tyre_set_name=self.list_tyre_set_name[tyre_set_idx]
        self.tyre_set_base_reliability_percent_loss_per_lap=self.list_tyre_set_base_reliability_percent_loss_per_lap[tyre_set_idx]
        self.tyre_set_optimal_temperature_celcius=self.list_tyre_set_optimal_temperature_celcius[tyre_set_idx]
        self.tyre_set_relative_speed_loss_km_hr=self.list_tyre_set_relative_speed_loss_km_hr[tyre_set_idx]

    def reset_tyre_stat(self):
        self.tyre_reliability_percent=100
        self.tyre_temperature_celcius=self.tyre_set_optimal_temperature_celcius
        self.tyre_temperature_memory_celcius=deque(maxlen=MEMORY_SIZE)

    def decrease_tyre_reliability(self, diff_tyre_reliability_percent:int|float):
        assert diff_tyre_reliability_percent>=0

        self.tyre_reliability_percent=max(0,self.tyre_reliability_percent-diff_tyre_reliability_percent)

    def measure_tyre_temperature(self, track_temperature_celcius:int|float, brake_temperature_celcius:int|float):
        # calculate tyre temperature based on track temperature, brake temperature, and memory of tyre temperature
        self.tyre_temperature_memory_celcius.append(self.tyre_temperature_celcius)
        temp_pure_tyre_temperature_celcius=(self.tyre_set_optimal_temperature_celcius+track_temperature_celcius+1*brake_temperature_celcius)/3
        self.tyre_temperature_celcius=(sum(self.tyre_temperature_memory_celcius)+temp_pure_tyre_temperature_celcius)/(len(self.tyre_temperature_memory_celcius)+1)

    def calculate_tyre_relative_speed_loss(self):
        # tyre_relative_speed_loss ~ base_speed_loss*ratio_to_optimal_temperature+reliability
        self.tyre_relative_speed_loss_km_hr=self.tyre_set_relative_speed_loss_km_hr*(0.5*abs(self.tyre_temperature_celcius-self.tyre_set_optimal_temperature_celcius))+0.15*(100-self.tyre_reliability_percent)