import pyglet
from pyglet import gl
from physics import dt
import car
from pyglet.window import Window


pyglet.resource.path = ['./resources']
pyglet.resource.reindex()

window = Window(1024, 600)
gl.glClearColor(1, 1, 1, 1)
key_handler = pyglet.window.key.KeyStateHandler()
window.push_handlers(key_handler)
car1 = car.Car(handler=key_handler, player=2, image='bluecar')
car2 = car.Car(position=[1024-50, 100], rotation=180, handler=key_handler)
cars = [car1,car2]



@window.event
def on_draw():
    window.clear()
    for car in cars:
        car.sprite.draw()


@window.event
def update(dt):
    for car in cars:
        car.update(dt)
        car.sprite.draw()



pyglet.clock.schedule_interval(update, dt)
pyglet.app.run()
