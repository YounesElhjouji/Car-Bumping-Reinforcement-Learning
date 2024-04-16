from controller import handle_key_input
from entities.car_collection import CarCollection
from entities.world import World
from interfaces.pyglet_interface import PygletInterface, add_car
import physics
from utils.pyglet import PygletUtils
from utils.shaper import ShapeUtils


def on_update(dt):
    World.current_time += dt
    for car in CarCollection.cars:
        ShapeUtils.draw_debug_visuals(car=car, batch=PygletInterface.batch)
        handle_key_input(car)
        physics.move(car.body)
        physics.refill_turbo(car.body)
        PygletUtils.set_car_sprite_position(car)
        PygletUtils.set_fire_position(car)
        car.body.is_turbo = False


add_car(position=[512, 300])
PygletInterface.setup(on_update=on_update)
