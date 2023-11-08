import pytest

from models.engine import Engine

class TestEngine:
    def setup_method(self):
        self.engine=Engine()

    def test_is_not_usable_at_first(self):
        assert self.engine.is_usable()==False

    def test_config_engine_mode(self):
        list_engine_mode_name=['neutral',2,3,4,5,6,7,8,9,'party']
        list_engine_mode_base_reliability_percent_loss_per_lap=[1,2,3,4,5,6,7,8,9,10]
        list_engine_mode_base_maximum_horsepower=[10,20,30.2,50,100,200,300,400,700,760]
        list_engine_mode_fuel_volume_consuming_kg_per_lap=[2,5,8,3,6,9,1,4,7,10.8]
        list_engine_mode_temperature_celcius=[100,300,500,500,800,700,900,600,2000.2,2500.1]

        self.engine.config_engine_mode(list_engine_mode_name,list_engine_mode_base_reliability_percent_loss_per_lap,list_engine_mode_base_maximum_horsepower,list_engine_mode_fuel_volume_consuming_kg_per_lap,list_engine_mode_temperature_celcius)

        assert self.engine.list_engine_mode_name==list_engine_mode_name
        assert self.engine.list_engine_mode_base_reliability_percent_loss_per_lap==list_engine_mode_base_reliability_percent_loss_per_lap
        assert self.engine.list_engine_mode_base_maximum_horsepower==list_engine_mode_base_maximum_horsepower
        assert self.engine.list_engine_mode_fuel_volume_consuming_kg_per_lap==list_engine_mode_fuel_volume_consuming_kg_per_lap
        assert self.engine.list_engine_mode_temperature_celcius==list_engine_mode_temperature_celcius

    def test_set_init_fuel_volume(self):
        fuel_volume_kg=100
        self.engine.set_init_fuel_volume(fuel_volume_kg)

        assert self.engine.engine_fuel_volume_kg==fuel_volume_kg

    def test_decrease_fuel_volume_negative(self):
        self.test_set_init_fuel_volume()
        diff_fuel_volume_kg=-10000

        with pytest.raises(Exception) as e:
            self.engine.decrease_fuel_volume(diff_fuel_volume_kg)

    def test_decrease_fuel_volume(self):
        self.test_set_init_fuel_volume()
        fuel_volume_kg=self.engine.engine_fuel_volume_kg
        diff_fuel_volume_kg=10
        self.engine.decrease_fuel_volume(diff_fuel_volume_kg)

        assert self.engine.engine_fuel_volume_kg==fuel_volume_kg-diff_fuel_volume_kg

    def test_decrease_engine_reliability_negative(self):
        diff_engine_reliability_percent=-10000

        with pytest.raises(Exception) as e:
            self.engine.decrease_engine_reliability(diff_engine_reliability_percent)

    def test_decrease_engine_reliability(self):
        diff_engine_reliability_percent=10
        self.engine.decrease_engine_reliability(diff_engine_reliability_percent)

        assert self.engine.engine_reliability_percent==100-diff_engine_reliability_percent

    def test_set_engine_mode(self):
        self.test_config_engine_mode()
        inspected_engine_mode='neutral'
        self.engine.set_engine_mode(inspected_engine_mode)

        assert self.engine.engine_mode_name=='neutral'
        assert self.engine.engine_mode_base_reliability_percent_loss_per_lap==1
        assert self.engine.engine_mode_base_maximum_horsepower==10
        assert self.engine.engine_mode_fuel_volume_consuming_kg_per_lap==2
        assert self.engine.engine_mode_temperature_celcius==100

    def test_set_engine_mode_second(self):
        self.test_set_engine_mode()
        inspected_engine_mode=9
        self.engine.set_engine_mode(inspected_engine_mode)

        assert self.engine.engine_mode_name==9
        assert self.engine.engine_mode_base_reliability_percent_loss_per_lap==9
        assert self.engine.engine_mode_base_maximum_horsepower==700
        assert self.engine.engine_mode_fuel_volume_consuming_kg_per_lap==7
        assert self.engine.engine_mode_temperature_celcius==2000.2

    def test_measure_engine_temperature(self):
        self.test_set_engine_mode()
        self.engine.measure_engine_temperature()

        assert self.engine.engine_temperature_celcius==75

    def test_measure_engine_temperature_second(self):
        self.test_set_engine_mode()
        self.engine.measure_engine_temperature()
        self.engine.set_engine_mode(5)
        self.engine.measure_engine_temperature()

        assert self.engine.engine_temperature_celcius==925/3

    def test_measure_engine_temperature_third(self):
        self.test_set_engine_mode()
        self.engine.measure_engine_temperature()
        self.engine.set_engine_mode(5)
        self.engine.measure_engine_temperature()
        self.engine.set_engine_mode('party')
        self.engine.measure_engine_temperature()

        assert self.engine.engine_temperature_celcius==(50+75+925/3+2500.1)/4

    def test_measure_engine_temperature_forth(self):
        self.test_set_engine_mode()
        self.engine.measure_engine_temperature()
        self.engine.set_engine_mode(5)
        self.engine.measure_engine_temperature()
        self.engine.set_engine_mode('party')
        self.engine.measure_engine_temperature()
        self.engine.set_engine_mode(2)
        self.engine.measure_engine_temperature()

        assert self.engine.engine_temperature_celcius==(75+925/3+(50+75+925/3+2500.1)/4+300)/4

    def test_is_usable_positive(self):
        self.test_set_init_fuel_volume()

        assert self.engine.is_usable()==True

    def test_is_usable_negative_lag_fuel(self):
        self.test_set_init_fuel_volume()
        self.engine.decrease_fuel_volume(100)

        assert self.engine.is_usable()==False

    def test_is_usable_negative_lag_reliability(self):
        self.test_set_init_fuel_volume()
        self.engine.decrease_engine_reliability(100)

        assert self.engine.is_usable()==False