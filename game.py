from random import randint
from entities.car_collection import CarCollection
from entities.enums import Player
from entities.world import World
from interfaces.pyglet_interface import PygletInterface, add_car
import physics
from utils.pyglet import PygletUtils
from utils.shaper import ShapeUtils
from controller import control_car


def on_update(dt):
    World.current_time += dt
    physics.check_collisions()
    for car in CarCollection.cars:
        ShapeUtils.draw_debug_visuals(car=car, batch=PygletInterface.batch)
        control_car(car)
        physics.move(car.body)
        physics.refill_turbo(car.body)
        PygletUtils.set_car_sprite_position(car)
        PygletUtils.set_fire_position(car)
        car.body.is_turbo = False


add_car(position=[512, 300])

add_car(position=[700, 300], rotation=90, player=Player.P2)
for _ in range(10):
    add_car(
        position=[randint(0, World.size[0] - 100), randint(0, World.size[1] - 100)],
        rotation=randint(0, 359),
        player=Player.RANDOM,
    )
#
PygletInterface.start_game(on_update=on_update)
