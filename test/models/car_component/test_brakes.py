import pytest

from models.car_component.brakes import Brakes

class TestBrakes:
    def setup_method(self):
        self.brakes=Brakes()

    def test_is_usable_at_first(self):
        assert self.brakes.is_usable()==True

    def test_init_brake_mode(self):
        DICT_BRAKE_MODE={
            'list_brake_mode_name':[
                'Neutral',
                'Warm',
                'Fly',
                1,
                2,
                3,
                4,
                5,
                'PitEntry',
                'PitExit',
                6,
                7,
                8,
                9,
                'Def',
                'Full',
            ],
            'list_brake_mode_base_brake_pressure_psi':[
                800,
                1000,
                950,
                1100,
                1150,
                1200,
                1250,
                1300,
                900,
                850,
                1400,
                1450,
                1500,
                1600,
                1750,
                2000,
            ],
            'list_brake_mode_base_brake_temperature_celcius':[
                300,
                800,
                450,
                500,
                525,
                550,
                575,
                600,
                350,
                425,
                625,
                650,
                675,
                689,
                750,
                1000,
            ],
            'list_brake_mode_base_reliability_percent_loss_per_lap':[
                0.063131313,
                1.48989899,
                0.568181818,
                0.757575758,
                0.795454545,
                0.833333333,
                0.871212121,
                0.909090909,
                0.315656566,
                0.323232323,
                0.631313131,
                1.047979798,
                1.085858586,
                1.199494949,
                1.891414141,
                3.787878788
            ]
        }

        self.brakes.init_brake_mode(**DICT_BRAKE_MODE)

        assert self.brakes.list_brake_mode_name==DICT_BRAKE_MODE['list_brake_mode_name']
        assert self.brakes.list_brake_mode_base_brake_pressure_psi==DICT_BRAKE_MODE['list_brake_mode_base_brake_pressure_psi']
        assert self.brakes.list_brake_mode_base_brake_temperature_celcius==DICT_BRAKE_MODE['list_brake_mode_base_brake_temperature_celcius']
        assert self.brakes.list_brake_mode_base_reliability_percent_loss_per_lap==DICT_BRAKE_MODE['list_brake_mode_base_reliability_percent_loss_per_lap']

    def test_set_brake_mode(self):
        self.test_init_brake_mode()
        self.brakes.set_brake_mode('Fly')

        assert self.brakes.brake_mode_name=='Fly'
        assert self.brakes.brake_mode_base_brake_pressure_psi==950
        assert self.brakes.brake_mode_base_brake_temperature_celcius==450
        assert self.brakes.brake_mode_base_reliability_percent_loss_per_lap==0.568181818

    def test_decrease_brake_reliability(self):
        assert self.brakes.brake_reliability_percent==100

        self.brakes.decrease_brake_reliability(100)

        assert self.brakes.brake_reliability_percent==0

    def test_measure_brake_temperature(self):
        self.test_set_brake_mode()
        self.brakes.measure_brake_temperature()

        assert self.brakes.brake_temperature_celcius==245

    def test_measure_brake_pressure(self):
        self.test_set_brake_mode()
        self.brakes.measure_brake_pressure()

        assert self.brakes.brake_pressure_psi==949.6

    def test_is_usable_final_negative(self):
        self.test_decrease_brake_reliability()

        assert self.brakes.is_usable()==False