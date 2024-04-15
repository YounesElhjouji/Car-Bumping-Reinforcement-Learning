from math import cos, radians, sin

import numpy as np
from pyglet.graphics import Batch
from pyglet.sprite import Sprite
from pyglet.window import key

from entities.body import Body
import physics
from physics import bump_objects, dt, world_size
from utils.pyglet import PygletUtils
from utils.shaper import ShaperUtils

car_width = 40

cars = []
collision_matrix = np.zeros(shape=world_size, dtype=int)


class Car(object):
    number_of_cars = 0

    def __init__(
        self,
        handler,
        batch: Batch,
        position: np.ndarray | None = None,
        rotation=80,
        player=1,
    ):
        self.id = Car.number_of_cars
        Car.number_of_cars += 1
        self.key_handler = handler
        self.player = player

        self.batch = batch
        self.car_sprite: Sprite = PygletUtils.create_car_sprite(
            width=car_width, batch=batch
        )
        self.fire_sprite = PygletUtils.create_fire_sprite(
            car_height=self.car_sprite.height, batch=batch
        )
        self.body = Body(
            width=self.car_sprite.width,
            height=self.car_sprite.height,
            position=position,
        )
        self.car_sprite.x = self.body.position[0]
        self.car_sprite.y = self.body.position[1]
        self.car_sprite.rotation = rotation

        self.debug_visuals = {}

    @property
    def center(self):
        return np.array(
            [
                self.body.position[0] + 0.5 * get_portion(self, is_x=True),
                self.body.position[1] + 0.5 * get_portion(self, is_x=False),
            ]
        )

    def update(self):
        if (
            physics.current_time % self.body.turbo_cooldown == 0
            and self.body.turbo_fuel < self.body.turbo_capacity
        ):
            self.body.turbo_fuel += 8
        self.body.thrust = 0
        self.fire_sprite.visible = False
        self.get_player_input()
        physics.move(self.body)
        print(f"Body position: {self.body.position}")
        self.car_sprite.x = self.body.position[0]
        self.car_sprite.y = self.body.position[1]
        self.set_fire_position()
        self.car_sprite.rotation = -self.body.rotation

    def set_fire_position(self):
        self.fire_sprite.rotation = self.car_sprite.rotation
        self.fire_sprite.x = self.car_sprite.x - (
            self.car_sprite.width * 1.12
        ) * np.cos(np.radians(self.body.rotation))
        self.fire_sprite.y = self.car_sprite.y - (
            self.car_sprite.width * 1.12
        ) * np.sin(np.radians(self.body.rotation))

    def get_player_input(self):
        if self.player == 1:
            up = self.key_handler[key.UP]
            down = self.key_handler[key.DOWN]
            left = self.key_handler[key.LEFT]
            right = self.key_handler[key.RIGHT]
            turbo = self.key_handler[key.M]
        else:
            up = self.key_handler[key.W]
            down = self.key_handler[key.S]
            left = self.key_handler[key.A]
            right = self.key_handler[key.D]
            turbo = self.key_handler[key.LSHIFT]

        if up:
            self.go_forward()
        if down:
            self.go_backwards()
        if turbo:
            self.run_turbo()
        if left:
            self.turn_left()
        if right:
            self.turn_right()
        if (not left) and (not right) and 0 < abs(self.body.steer):
            self.body.steer += 100 * dt if self.body.steer < 0 else -100 * dt

    def go_forward(self):
        self.body.thrust = 1300

    def go_backwards(self):
        if self.body.speed > 10:
            self.body.thrust = -1300
        else:
            self.body.thrust = -800

    def run_turbo(self):
        if self.body.turbo_fuel > 0:
            self.fire_sprite.visible = True
            self.body.turbo_fuel -= 1
            self.body.thrust += 10000

    def turn_left(self):
        if self.body.steer < self.body.max_steer:
            self.body.steer += 100 * dt

    def turn_right(self):
        if self.body.steer > -self.body.max_steer:
            self.body.steer -= 100 * dt

    def draw_debug_visuals(self):
        px, py = self.body.position
        x, y = self.center
        center = ShaperUtils.get_point(x=x, y=y, color="green", batch=self.batch)
        pos = ShaperUtils.get_point(x=px, y=py, color="red", batch=self.batch)
        self.debug_visuals.update({"pos": pos, "center": center})


def check_collisions():
    for car1 in cars:
        for car2 in cars:
            if car1 == car2:
                continue
            if two_cars_collide(car1, car2):
                print(f"Boom!! {car1.id} and {car2.id} collide")
                bump_objects(car1, car2)


def two_cars_collide(car1: Car, car2: Car) -> bool:
    # Calculate the distance between the car centers
    distance_x = abs(car1.center[0] - car2.center[0])
    distance_y = abs(car1.center[1] - car2.center[1])
    # Check for overlap in both x and y directions
    overlap_x = (
        distance_x < (get_portion(car1, is_x=True) + get_portion(car2, is_x=True)) / 2
    )
    overlap_y = (
        distance_y < (get_portion(car1, is_x=False) + get_portion(car2, is_x=False)) / 2
    )
    # If there is overlap in both x and y, the cars are colliding
    print(f"Overlap X: {overlap_x}, Overlap Y: {overlap_y}")
    if overlap_x and overlap_y:
        pass
    return overlap_x and overlap_y


def get_portion(car: Car, is_x: bool):
    width = car.car_sprite.width
    height = car.car_sprite.height
    angle = radians(car.body.rotation)
    if is_x:
        return width * cos(angle) - height * sin(angle)
    else:
        return width * sin(angle) + height * cos(angle)
