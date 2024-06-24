import math
from random import randint
import numpy as np
from bson import ObjectId
from pyglet.sprite import Sprite

from entities.state import State
from entities.enums import Player
from entities.body import Body
from entities.sensor import Sensor
from entities.world import World
from dqn.agent import QNetAgent
from ppo.agent import PPOAgent


class Car(object):
    def __init__(
        self,
        car_sprite: Sprite,
        fire_sprite: Sprite,
        position: np.ndarray | None = None,
        rotation=80,
        player: Player = Player.P1,
        agent: QNetAgent | PPOAgent | None = None,
    ):
        self.id_ = ObjectId()
        self.player = player
        self.car_sprite = car_sprite
        self.fire_sprite = fire_sprite
        self.body = Body(
            width=self.car_sprite.width,
            height=self.car_sprite.height,
            position=position,
            rotation=rotation,
        )
        self.debug_visuals = {}
        self.metadata = {}  # Can be used by modules to store metadata
        self.wall_sensors = self.create_sensors()
        self.car_sensors = self.create_sensors()
        self.bumper_sensors = self.create_sensors()
        self.sensors: list[Sensor] = []
        self.reward = 0
        self.agent = QNetAgent([14, 9]) if agent is None else agent
        self.score = 0
        self.touches_wall = False
        self.last_reset = World.current_time

    def create_sensors(self) -> list[Sensor]:
        sensors: list[Sensor] = []
        front_sensors, back_sensors = 7, 3
        for offset in np.linspace(-30, 30, front_sensors):
            sensors.append(
                Sensor(
                    position=self.body.car_rect.center,
                    rotation=self.body.rotation,
                    angle_offset=offset,
                )
            )
        for offset in np.linspace(150, 210, back_sensors):
            sensors.append(
                Sensor(
                    position=self.body.car_rect.center,
                    rotation=self.body.rotation,
                    angle_offset=offset,
                )
            )
        return sensors

    def update_sensors(self):
        sensors = self.wall_sensors + self.car_sensors + self.bumper_sensors
        for sensor in sensors:
            sensor.update_sensor(
                position=self.body.car_rect.center, rotation=self.body.rotation
            )

    def set_reward(self):
        # Distance to wall reward
        wall_distance_punishment = self.punish_wall_proximity(
            self.body.car_rect.center, World.np_size
        )

        # # Speed reward
        # speed_reward = min(self.body.speed / 100, 2.0)
        # adjusted_speed_reward = (1 + wall_distance_punishment) * speed_reward

        # Wall bump penalty
        wall_touch_punishment = -50.0 if self.touches_wall else 0.0

        # total reward
        self.reward = wall_distance_punishment + wall_touch_punishment
        self.update_score()

    @staticmethod
    def punish_wall_proximity(position: np.ndarray, world_size: np.ndarray) -> float:
        punishment = (np.abs(position - world_size / 2) - world_size / 4) / (
            world_size / 2
        )
        punishment = np.clip(-punishment, a_min=-np.inf, a_max=0.0)
        return punishment.sum()

    def get_state(self):
        radians = math.radians(self.body.rotation)
        dx = math.cos(radians)
        dy = math.sin(radians)
        return State(
            x=self.body.position[0] / World.size[0],
            y=self.body.position[1] / World.size[1],
            speed=self.body.speed / World.size[1],
            direction=self.body.direction,
            dx=dx,
            dy=dy,
            vx=self.body.velocity[0] / World.size[1],
            vy=self.body.velocity[1] / World.size[1],
            wall_sensors=[sensor.value for sensor in self.wall_sensors],
        )

    def get_agent(self):
        return self.agent

    def update_score(self):
        self.score = self.score + self.reward

    def reset(self):
        dist = 40
        self.body.position = np.array(
            [
                randint(dist, World.size[0] - dist),
                randint(dist, World.size[1] - dist),
            ]
        )
        self.body.rotation = randint(0, 360)
        self.body.reset_physics()
        self.score = 0
        self.touches_wall = False
        self.last_reset = World.current_time


if __name__ == "__main__":
    size = [600, 420]
    pos = [600, 0]
    punishment = Car.punish_wall_proximity(np.array(pos), np.array(size))
    print(punishment)
