import numpy as np
import matplotlib.pyplot as plt
from random import randint

from entities.car_collection import CarCollection
from entities.enums import Player
from entities.world import World
from game.pyglet_interface import PygletInterface, create_car
import game.physics as physics
from dqn.agent import QNetAgent
from game.utils.pyglet import PygletUtils
from game.utils.sensing import SensingUtils
from game.utils.shaper import ShapeUtils
from game.controller import control_car


def play():
    collection= CarCollection(cars=[create_car(position=[512, 300])])

    def on_update(dt):
        for car in collection.cars:
            car.reward = 0
            control_car(car)
        physics.on_update(collection)
        for car in collection.cars:
            car.update_sensors()
            PygletUtils.set_car_sprite_position(car)
            PygletUtils.set_fire_position(car)
            ShapeUtils.draw_debug_visuals(car=car, batch=PygletInterface.batch)
            SensingUtils.sense_walls(car, batch=PygletInterface.batch)
            SensingUtils.sense_cars(
                car=car, car_collection=collection, batch=PygletInterface.batch
            )
            PygletUtils.draw_sensors(car=car, batch=PygletInterface.batch)
        # SensingUtils.debug_line_intersection(batch=PygletInterface.batch)

    PygletInterface.start_(on_update=on_update)

if __name__ == "__main__":
    play()
