import numpy as np
from bson import ObjectId
from pyglet.sprite import Sprite

from entities.enums import Player
from entities.body import Body
from entities.sensor import Sensor


class Car(object):
    def __init__(
        self,
        car_sprite: Sprite,
        fire_sprite: Sprite,
        position: np.ndarray | None = None,
        rotation=80,
        player: Player = Player.P1,
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
        self.sensors: list[Sensor] = []
        n_sensors = 7
        for offset in np.linspace(-30, 30, n_sensors):
            self.sensors.append(
                Sensor(body=self.body, car_id=self.id_, angle_offset=offset)
            )

    def update_sensors(self):
        for sensor in self.sensors:
            sensor.update_sensor(self.body)
