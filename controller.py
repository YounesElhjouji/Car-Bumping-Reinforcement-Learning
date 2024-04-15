from pyglet.window import key
from car import Car
from interfaces.pyglet_interface import PygletInterface
import physics


def handle_key_input(car: Car):
    key_handler = PygletInterface.key_handler
    if car.player == 1:
        up = key_handler[key.UP]
        down = key_handler[key.DOWN]
        left = key_handler[key.LEFT]
        right = key_handler[key.RIGHT]
        turbo = key_handler[key.M]
    else:
        up = key_handler[key.W]
        down = key_handler[key.S]
        left = key_handler[key.A]
        right = key_handler[key.D]
        turbo = key_handler[key.LSHIFT]

    if up:
        physics.go_forward(car.body)
    if down:
        physics.go_backwards(car.body)
    if turbo:
        physics.run_turbo(car.body)
    if left:
        physics.turn_left(car.body)
    if right:
        physics.turn_right(car.body)
    if (not left) and (not right) and 0 < abs(car.body.steer):
        physics.reverse_steer(car.body)
    if (not up) and (not down):
        physics.cancel_thrust(car.body)
