import pytest

from models.car_component.tyres import Tyres

class TestBrakes:
    def setup_method(self):
        self.tyres=Tyres()

    def test_init_tyre_set(self):
        DICT_TYRE_SET={
            'list_tyre_set_name':[
                'Soft',
                'Medium',
                'Hard'
            ],
            'list_tyre_set_base_reliability_percent_loss_per_lap':[
                5.611672278,
                4.329004329,
                3.885003885,
            ],
            'list_tyre_set_optimal_temperature_celcius':[
                100,
                115,
                132,
            ],
            'list_tyre_set_relative_speed_loss_km_hr':[
                0,
                4.5,
                6.8
            ]
        }

        self.tyres.init_tyre_set(**DICT_TYRE_SET)

        assert self.tyres.list_tyre_set_name==DICT_TYRE_SET['list_tyre_set_name']
        assert self.tyres.list_tyre_set_base_reliability_percent_loss_per_lap==DICT_TYRE_SET['list_tyre_set_base_reliability_percent_loss_per_lap']
        assert self.tyres.list_tyre_set_optimal_temperature_celcius==DICT_TYRE_SET['list_tyre_set_optimal_temperature_celcius']
        assert self.tyres.list_tyre_set_relative_speed_loss_km_hr==DICT_TYRE_SET['list_tyre_set_relative_speed_loss_km_hr']

    def test_set_tyre_set(self):
        self.test_init_tyre_set()
        self.tyres.set_tyre_set('Soft')

        assert self.tyres.tyre_set_name=='Soft'
        assert self.tyres.tyre_set_base_reliability_percent_loss_per_lap==5.611672278
        assert self.tyres.tyre_set_optimal_temperature_celcius==100
        assert self.tyres.tyre_set_relative_speed_loss_km_hr==0

    def test_decrease_tyre_reliability(self):
        assert self.tyres.tyre_reliability_percent==100

        self.tyres.decrease_tyre_reliability(100)

        assert self.tyres.tyre_reliability_percent==0

    def test_measure_tyre_temperature(self):
        self.test_set_tyre_set()
        self.tyres.measure_tyre_temperature(30,2600)

        assert self.tyres.tyre_temperature_celcius==180

    def test_calculate_tyre_relative_speed_loss(self):
        self.test_measure_tyre_temperature()
        self.tyres.calculate_tyre_relative_speed_loss()

        assert self.tyres.tyre_relative_speed_loss_km_hr==0

    def test_reset_tyre_stat(self):
        self.test_set_tyre_set()
        self.test_decrease_tyre_reliability()

        self.tyres.set_tyre_set("Hard")
        self.tyres.reset_tyre_stat()

        assert self.tyres.tyre_reliability_percent==100
        assert self.tyres.tyre_temperature_celcius==132
        assert len(self.tyres.tyre_temperature_memory_celcius)==0