"""Represents a physical body"""

import numpy as np

from entities.world import World


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

        self.force = 0.0
        self.thrust = 0.0
        self.steer = 0.0
        self.mass = 10
        self.friction = self.mass * 9.81 * friction_coefficient
        self.max_steer = 20.0

        self.is_turbo = False
        self.turbo_capacity = 40
        self.turbo_cooldown = 50 * World.dt
        self.turbo_fuel = self.turbo_capacity

    @property
    def speed(self) -> float:
        return float(np.linalg.norm(self.velocity))
