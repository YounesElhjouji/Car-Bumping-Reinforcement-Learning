from car import Car
from utils.utils import get_window_size


class World:
    size = get_window_size()
    cars: list[Car] = []
    dt = 0.01
