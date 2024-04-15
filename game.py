from entities.world import World
from interfaces.pyglet_interface import PygletInterface, add_car
import physics


def on_update(dt):
    physics.current_time += 1
    for car in World.cars:
        car.draw_debug_visuals()
        car.update()


World()
add_car(position=[512, 300])
PygletInterface.setup(on_update=on_update)
