import pytest

from models.car_component.brakes import Brakes

class TestBrakes:
    def setup_method(self):
        self.brakes=Brakes()

    def test_is_usable_at_first(self):
        assert self.brakes.is_usable()==True