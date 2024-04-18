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

    @property
    def center(self) -> np.ndarray:
        """Calculates the center of the rectangle."""
        x_coords = [p[0] for p in self.points]
        y_coords = [p[1] for p in self.points]
        return np.array([np.mean(x_coords), np.mean(y_coords)])
