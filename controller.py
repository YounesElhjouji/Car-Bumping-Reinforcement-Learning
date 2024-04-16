from pyglet.window import key
from car import Car
from entities.enums import Player
from interfaces.pyglet_interface import PygletInterface
import physics

from dataclasses import dataclass


@dataclass
class ControlInput:
    up: bool
    down: bool
    left: bool
    right: bool
    turbo: bool


def get_control_input(car: Car) -> ControlInput:
    key_handler = PygletInterface.key_handler
    if car.player == Player.P1:
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
    return ControlInput(up=up, down=down, left=left, right=right, turbo=turbo)


def control_car(car: Car):
    inp = get_control_input(car)
    if inp.up:
        physics.go_forward(car.body)
    if inp.down:
        physics.go_backwards(car.body)
    if inp.turbo:
        physics.run_turbo(car.body)
    if inp.left:
        physics.turn_left(car.body)
    if inp.right:
        physics.turn_right(car.body)
    if (not inp.left) and (not inp.right) and 0 < abs(car.body.steer):
        physics.reverse_steer(car.body)
    if (not inp.up) and (not inp.down):
        physics.cancel_thrust(car.body)
