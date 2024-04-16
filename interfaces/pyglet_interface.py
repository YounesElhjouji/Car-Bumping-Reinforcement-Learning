from typing import Callable
import numpy as np
import pyglet
from pyglet import gl
from pyglet.graphics import Batch
from pyglet.window import Window

from car import Car
from entities.car_collection import CarCollection
from entities.world import World
from utils.pyglet import PygletUtils
from utils.utils import get_world_size


class PygletInterface:
    batch = Batch()
    pyglet.resource.path = ["./resources"]
    pyglet.resource.reindex()
    world_size = get_world_size()
    window = Window(World.size[0], World.size[1])
    gl.glClearColor(1, 1, 1, 1)
    key_handler = pyglet.window.key.KeyStateHandler()
    window.push_handlers(key_handler)

    @classmethod
    def setup(cls, on_update: Callable):
        @cls.window.event
        def on_draw():
            cls.window.clear()
            cls.batch.draw()
            gl.glFlush()

        @cls.window.event
        def update(dt):
            on_update(dt)

        pyglet.clock.schedule_interval(update, World.dt)
        pyglet.app.run()


def add_car(position: list[int], rotation: int = 0, player: int = 1) -> None:
    batch = PygletInterface.batch
    car_sprite = PygletUtils.create_car_sprite(width=World.car_width, batch=batch)
    fire_sprite = PygletUtils.create_fire_sprite(
        car_height=car_sprite.height, batch=batch
    )

    CarCollection.cars.append(
        Car(
            position=np.array(position),
            rotation=rotation,
            car_sprite=car_sprite,
            fire_sprite=fire_sprite,
            player=player,
        )
    )
