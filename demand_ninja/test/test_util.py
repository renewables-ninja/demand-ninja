import pytest
import pandas as pd

import demand_ninja
from demand_ninja.util import smooth_temperature, get_cdd, get_hdd


class TestUtil:
    def test_smooth_temperature(self):
        temperature = pd.Series([0, 0, 1, 1, 1, 0.5, 0, 0, 0, 1, 2, 3, 4])
        smoothing = [0.50, 0.25]
        smoothed_temperature = pd.Series(
            [
                0,
                0,
                0.5714,
                0.8571,
                1,
                0.7143,
                0.2857,
                0.0714,
                0,
                0.5714,
                1.4286,
                2.4286,
                3.4286,
            ]
        )
        pd.testing.assert_series_equal(
            smooth_temperature(temperature, smoothing).round(4), smoothed_temperature
        )

    def test_get_hdd(self):
        assert get_hdd([-10, 0, 10, 20, 30], 14) == [24, 14, 4, 0, 0]

    def test_get_cdd(self):
        assert get_cdd([-10, 0, 10, 20, 30], 14) == [0, 0, 0, 6, 16]
