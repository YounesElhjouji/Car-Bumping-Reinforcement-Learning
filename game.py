import pyglet
from pyglet import gl
from physics import dt, world_size
import car
from pyglet.window import Window
car_width = 24

# Init and get resources
pyglet.resource.path = ['./resources']
pyglet.resource.reindex()
image = pyglet.resource.image('car1' + '.png')
car_sprite = pyglet.sprite.Sprite(image)
car_sprite.scale = car_width/car_sprite.width
car_sprite.image.anchor_x = car_sprite.image.width / 2
image = pyglet.resource.image('fire' + '.png')
fire_sprite = pyglet.sprite.Sprite(image)
fire_sprite.anchor_x = fire_sprite.width
fire_sprite.anchor_y = fire_sprite.height / 2
fire_sprite.scale = 0.8 * car_sprite.height / fire_sprite.height


window = Window(world_size[0],world_size[1])
gl.glClearColor(1, 1, 1, 1)
key_handler = pyglet.window.key.KeyStateHandler()
window.push_handlers(key_handler)
cars = []
cars.append(car.Car(handler=key_handler, car_sprite=car_sprite, fire_sprite=fire_sprite))





@window.event
def on_draw():
    window.clear()
    for car in cars:
        car.sprite.draw()
    fire_sprite.draw()


@window.event
def update(dt):
    for car in cars:
        car.update(dt)
        car.sprite.draw()



pyglet.clock.schedule_interval(update, dt)
pyglet.app.run()
