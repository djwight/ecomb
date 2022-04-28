from math import isclose
import numpy as np
from HausFinder.utils import time_in_mins, check_internet_connection


def test_time_in_mins() -> None:
    assert type(time_in_mins(60)) == np.float64, "Failed: wrong dtype returned"
    assert isclose(time_in_mins(60), 1.00), "Failed: 60s did not equal 1.00 mins!"
    assert isclose(time_in_mins(90), 1.50), "Failed: 90s did not equal 1.50 mins!"


def test_check_internet_connection() -> None:
    assert check_internet_connection() == "OK: 200"
