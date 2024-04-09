from math import cos, radians, sin

import numpy as np
from pyglet.graphics import Batch
from pyglet.resource import image
from pyglet.sprite import Sprite
from pyglet.window import key

import physics
from physics import bump_objects, dt, friction_coefficient, world_size
from utils.shaper import Shaper

car_width = 120

cars = []
collision_matrix = np.zeros(shape=world_size, dtype=int)


class Car(object):
    number_of_cars = 0

    def __init__(
        self, handler, batch: Batch, position=[512, 300], rotation=80, player=1
    ):
        self.id = Car.number_of_cars
        Car.number_of_cars += 1
        self.turbo_capacity = 40
        self.turbo_cooldown = 50
        self.turbo_fuel = self.turbo_capacity

        self.key_handler = handler
        self.player = player
        self.max_steer = 20
        self.thrust = 0
        self.force = 0
        self.position = np.array(position)
        self.velocity = np.array([0.0, 0.0])
        self.speed = 0
        self.steer = 0
        self.mass = 10
        self.friction = self.mass * 9.81 * friction_coefficient
        self.direction = 1
        self.batch = batch

        my_image = image("car1" + ".png")
        car_sprite: Sprite = Sprite(img=my_image, batch=batch)
        car_sprite.scale = car_width / car_sprite.width
        car_sprite.image.anchor_x = car_sprite.width // 2
        car_sprite.image.anchor_y = car_sprite.height // 2
        print(f"width: {car_sprite.width}, height: {car_sprite.height}")
        print(
            f"Image: width: {car_sprite.image.width}, height: {car_sprite.image.height}"
        )

        my_image = image("fire" + ".png")
        fire_sprite = Sprite(my_image, batch=batch)
        fire_sprite.anchor_x = fire_sprite.width
        fire_sprite.anchor_y = fire_sprite.height / 2
        fire_sprite.scale = 0.8 * car_sprite.height / fire_sprite.height

        self.fire = fire_sprite
        self.sprite = car_sprite
        self.length = self.sprite.width
        self.sprite.x = self.position[0]
        self.sprite.y = self.position[1]
        self.sprite.rotation = rotation
        self.rotation = self.sprite.rotation

        self.size_circle = 5
        self.debug_visuals = {}

    @property
    def center(self):
        return np.array(
            [
                self.position[0] + 0.5 * get_portion(self, is_x=True),
                self.position[1] + 0.5 * get_portion(self, is_x=False),
            ]
        )

    def update(self):
        if (
            physics.current_time % self.turbo_cooldown == 0
            and self.turbo_fuel < self.turbo_capacity
        ):
            self.turbo_fuel += 8
        self.thrust = 0
        self.fire.visible = False
        self.get_player_input()
        physics.move(self)
        self.sprite.x = self.position[0]
        self.sprite.y = self.position[1]
        self.set_fire_position()
        self.sprite.rotation = -self.rotation

    def set_fire_position(self):
        self.fire.rotation = self.sprite.rotation
        self.fire.x = self.sprite.x - (self.sprite.width * 1.12) * np.cos(
            np.radians(self.rotation)
        )
        self.fire.y = self.sprite.y - (self.sprite.width * 1.12) * np.sin(
            np.radians(self.rotation)
        )

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
            self.thrust = 1300
        elif down and np.linalg.norm(self.velocity) > 10:
            self.thrust = -1300
        elif down:
            self.thrust = -800
        if turbo and self.turbo_fuel > 0:
            self.fire.visible = True
            self.turbo_fuel -= 1
            self.thrust += 10000
        if left and self.steer < self.max_steer:
            self.steer += 100 * dt
        elif right and self.steer > -self.max_steer:
            self.steer -= 100 * dt
        else:
            if self.steer > 0:
                self.steer -= 100 * dt
            elif self.steer < 0:
                self.steer += 100 * dt

    def draw_debug_visuals(self):
        px, py = self.position
        x, y = self.center
        center = Shaper.get_point(x=x, y=y, color="green", batch=self.batch)
        pos = Shaper.get_point(x=px, y=py, color="red", batch=self.batch)
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
    width = car.sprite.width
    height = car.sprite.height
    angle = radians(car.rotation)
    if is_x:
        return width * cos(angle) - height * sin(angle)
    else:
        return width * sin(angle) + height * cos(angle)
