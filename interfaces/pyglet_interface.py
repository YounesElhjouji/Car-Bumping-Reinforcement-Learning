from typing import Callable
import numpy as np
import pyglet
from pyglet import gl
from pyglet.graphics import Batch
from pyglet.window import Window

from car import Car
from entities.world import World
from utils.utils import get_window_size


class PygletInterface:
    batch = Batch()
    pyglet.resource.path = ["./resources"]
    pyglet.resource.reindex()
    world_size = get_window_size()
    window = Window(world_size[0], world_size[1])
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


def add_car(position: list[int]):
    World.cars.append(
        Car(
            handler=PygletInterface.key_handler,
            position=np.array(position),
            batch=PygletInterface.batch,
        )
    )
