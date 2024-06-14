import numpy as np
from bson import ObjectId
from pyglet.sprite import Sprite

from entities.action import State
from entities.enums import Player
from entities.body import Body
from entities.sensor import Sensor
from entities.world import World
from dqn.agent import Agent


class Car(object):
    def __init__(
        self,
        car_sprite: Sprite,
        fire_sprite: Sprite,
        position: np.ndarray | None = None,
        rotation=80,
        player: Player = Player.P1,
        agent: Agent | None = None,
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
        self.agent = Agent([14, 9]) if agent is None else agent
        self.score = 0

    def create_sensors(self) -> list[Sensor]:
        sensors: list[Sensor] = []
        front_sensors, back_sensors = 2, 2
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

    def punish_wall_bump(self):
        pass
        # self.reward -= 1.0
        # print(f"Touched the wall, reward {self.reward}")

    def reward_speed(self):
        # if self.body.speed > 10 and self.body.direction == 1.0:
        #     self.reward += 0.1
        self.reward += self.body.speed / 100
        # print(f"Speed reward {self.reward}")

    def get_state(self):
        return State(
            x=self.body.position[0] / World.size[0],
            y=self.body.position[1] / World.size[1],
            speed=self.body.speed / World.size[1],
            direction=self.body.direction,
            wall_sensors=[sensor.value for sensor in self.wall_sensors],
        )

    def get_agent(self):
        return self.agent

    def update_score(self):
        self.score = self.score + self.reward
