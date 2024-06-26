from math import radians
import numpy as np


class Sensor:
    length: int = 200

    def __init__(
        self,
        position: np.ndarray,
        rotation: float,
        angle_offset: float,
    ) -> None:
        self.position = position
        self.angle_offset = angle_offset
        self.rotation = rotation + angle_offset
        self.value: float = 1.0  # distance from the wall [0, 1]

    def update_sensor(self, position: np.ndarray, rotation: float):
        self.position = position
        self.rotation = rotation + self.angle_offset

    @property
    def points(self) -> list[np.ndarray]:
        line_start = self.position
        line_end = (
            line_start
            + np.array([np.cos(radians(self.rotation)), np.sin(radians(self.rotation))])
            * self.length
        )
        return [line_start, line_end]
