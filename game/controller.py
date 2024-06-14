from random import randint, random
from pyglet.window import key
from game.car import Car
from entities.enums import Player
from entities.world import World
from game.pyglet_interface import PygletInterface
import game.physics as physics

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
    elif car.player == Player.P2:
        up = key_handler[key.W]
        down = key_handler[key.S]
        left = key_handler[key.A]
        right = key_handler[key.D]
        turbo = key_handler[key.LSHIFT]
    else:
        return random_input(car)
    return ControlInput(up=up, down=down, left=left, right=right, turbo=turbo)


def random_input(car: Car) -> ControlInput:
    gas_controls = car.metadata.get("gas_controls", [])
    steer_controls = car.metadata.get("steer_controls", [])
    if len(gas_controls) == 0:
        r = random()
        if r > 0.3:
            length = randint(300, 500)
            gas_controls = ["up"] * length
        elif r > 0.2:
            length = randint(100, 200)
            gas_controls = ["none"] * length
        else:
            length = randint(100, 300)
            gas_controls = ["down"] * length
        car.metadata["gas_controls"] = gas_controls

    if len(steer_controls) == 0:
        r = random()
        if r > 0.8:
            length = randint(10, 100)
            steer_controls = ["left"] * length
        elif r > 0.6:
            length = randint(10, 100)
            steer_controls = ["right"] * length
        else:
            length = randint(100, 300)
            steer_controls = ["none"] * length
        car.metadata["steer_controls"] = steer_controls
    gas_control = gas_controls.pop()
    steer_control = steer_controls.pop()
    if abs(World.size[0] / 2 - car.body.position[0]) > World.size[0] / 2 - 90:
        steer_control = "right"
    if abs(World.size[1] / 2 - car.body.position[1]) > World.size[1] / 2 - 90:
        steer_control = "right"
    up = gas_control == "up"
    down = gas_control == "down"
    right = steer_control == "right"
    left = steer_control == "left"
    return ControlInput(up=up, down=down, left=left, right=right, turbo=False)


def control_car(car: Car):
    # if car.metadata.get("bump", False):
    #     return
    inp = get_control_input(car)
    if (not inp.left) and (not inp.right) and 0 < abs(car.body.steer):
        physics.reverse_steer(car.body)
    if (not inp.up) and (not inp.down):
        physics.cancel_thrust(car.body)
    if not inp.turbo:
        physics.cancel_turbo(car.body)
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
