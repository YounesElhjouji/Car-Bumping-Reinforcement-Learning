import numpy as np
from dataclasses import dataclass


@dataclass
class Rectangle:
    bot_left: np.ndarray
    bot_right: np.ndarray
    top_left: np.ndarray
    top_right: np.ndarray

    @property
    def points(self) -> list[np.ndarray]:
        return [self.bot_left, self.bot_right, self.top_right, self.top_left]
