"""Represents a physical body"""

import numpy as np

from utils.trigonometry import TrigUtils


friction_coefficient = 0.7


class Body:
    def __init__(
        self, width: int, height: int, position: np.ndarray | None = None, rotation=80
    ) -> None:
        if position is None:
            position = np.array([512, 600])
        self.position = np.array(position)
        self.velocity = np.array([0.0, 0.0])
        self.width = width
        self.height = height

        self.direction = 1
        self.rotation: float = rotation

        self.collision_force = np.array([0.0, 0.0])
        self.thrust = 0.0
        self.steer = 0.0
        self.mass = 10
        self.friction = self.mass * 9.81 * friction_coefficient
        self.max_steer = 20.0

        self.is_turbo = False
        self.turbo_capacity = 40
        self.turbo_cooldown = 4.0  # after each half second add a bit of fuel
        self.turbo_last_fuel = 0.0
        self.turbo_fuel = self.turbo_capacity

        self.rectangle = TrigUtils.get_rotated_rectangle(
            origin=position, width=width, height=height, angle=rotation
        )

    @property
    def speed(self) -> float:
        return float(np.linalg.norm(self.velocity))

    def update_rectangle(self):
        self.rectangle = TrigUtils.get_rotated_rectangle(
            origin=self.position,
            width=self.width,
            height=self.height,
            angle=self.rotation,
        )
