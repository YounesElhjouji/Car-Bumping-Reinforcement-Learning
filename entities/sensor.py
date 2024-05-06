from math import radians
from bson import ObjectId
import numpy as np


class Sensor:
    length: int = 200

    def __init__(
        self,
        position: np.ndarray,
        rotation: float,
        angle_offset: float,
        car_id: ObjectId,
    ) -> None:
        self.position = position
        self.angle_offset = angle_offset
        self.rotation = rotation + angle_offset
        self.car_id = car_id

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
