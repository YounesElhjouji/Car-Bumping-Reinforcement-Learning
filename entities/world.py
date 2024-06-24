from game.utils.utils import get_world_size
import numpy as np


class World:
    size = get_world_size()
    np_size = np.array(get_world_size())
    dt = 1 / 60  # 60 fps
    current_time = 0.0
    car_width = 40
