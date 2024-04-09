import pyglet
from pyglet import gl
from pyglet.graphics import Batch
from pyglet.window import Window

import physics
from car import Car, cars, check_collisions
from physics import dt, world_size

# Init and get resources
batch = Batch()
pyglet.resource.path = ["./resources"]
pyglet.resource.reindex()


window = Window(world_size[0], world_size[1])
gl.glClearColor(1, 1, 1, 1)
key_handler = pyglet.window.key.KeyStateHandler()
window.push_handlers(key_handler)
# for i in range(0, 1):
#     rotation = randint(0,360)
#     x = randint(50,world_size[0] - 50)
#     y = randint(50, world_size[1] - 50)
#     cars.append(car.Car(handler=key_handler, position=[x, y], player=-1, rotation=rotation, batch=batch))
cars.append(Car(handler=key_handler, position=[512, 300], batch=batch))


@window.event
def on_draw():
    window.clear()
    batch.draw()
    gl.glFlush()


@window.event
def update(dt):
    physics.current_time += 1
    for car in cars:
        car.draw_debug_visuals()
        car.update()
    check_collisions()


pyglet.clock.schedule_interval(update, dt)
pyglet.app.run()
