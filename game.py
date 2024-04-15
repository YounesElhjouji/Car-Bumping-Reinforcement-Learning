from controller import handle_key_input
from entities.car_collection import CarCollection
from entities.world import World
from interfaces.pyglet_interface import PygletInterface, add_car


def on_update(dt):
    World.current_time += dt
    for car in CarCollection.cars:
        car.draw_debug_visuals()
        handle_key_input(car)
        car.update()


World()
add_car(position=[512, 300])
PygletInterface.setup(on_update=on_update)
