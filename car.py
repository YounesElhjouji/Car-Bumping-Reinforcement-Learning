import numpy as np
from pyglet.sprite import Sprite

from entities.enums import Player
from entities.body import Body


class Car(object):
    def __init__(
        self,
        car_sprite: Sprite,
        fire_sprite: Sprite,
        position: np.ndarray | None = None,
        rotation=80,
        player: Player = Player.P1,
    ):
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
