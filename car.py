import pyglet
from pyglet.window import key
import numpy as np
import physics
from physics import dt, friction_coefficient, current_time, world_size
import math

car_width = 22

cars = []
collision_matrix = np.zeros(shape=world_size, dtype=int)



class Car(object):
    number_of_cars = 0

    def __init__(self, handler, position=[50, 100], rotation=0, player=1, batch=0):
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

        image = pyglet.resource.image('car1' + '.png')
        car_sprite = pyglet.sprite.Sprite(image, batch=batch)
        car_sprite.scale = car_width / car_sprite.width
        car_sprite.image.anchor_x = car_sprite.image.width / 2
        image = pyglet.resource.image('fire' + '.png')
        fire_sprite = pyglet.sprite.Sprite(image, batch=batch)
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

    def update(self, dt):
        if physics.current_time % self.turbo_cooldown == 0 and self.turbo_fuel < self.turbo_capacity:
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
        self.fire.x = self.sprite.x - (self.sprite.width * 1.12) * np.cos(np.radians(self.rotation))
        self.fire.y = self.sprite.y - (self.sprite.width * 1.12) * np.sin(np.radians(self.rotation))

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

def check_collisions():
    for car1 in cars:
        for car2 in cars:
            if car1 == car2:
                continue
            if np.linalg.norm(car1.position-car2.position) < 20:
                print('boom')
                #car1.velocity = 0.8 * car2.velocity

