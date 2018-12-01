import pyglet
from pyglet.window import key
import numpy as np
import physics
from physics import dt, friction_coefficient, t
import math


class Car(object):
    def __init__(self, handler, position=[50, 100],rotation=0, player=1, image='car', width=22):
        self.turbo_capacity = 10
        self.turbo_ccoldown = 20
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

        image = pyglet.resource.image(image+'.png')
        car_sprite = pyglet.sprite.Sprite(image, self.position[0], self.position[1])
        car_sprite.image.anchor_x = car_sprite.image.width / 2
        #car_sprite.image.anchor_y = car_sprite.image.height / 2
        car_sprite.rotation = rotation
        car_sprite.scale = width/car_sprite.width

        self.sprite = car_sprite
        self.rotation = self.sprite.rotation
        print(self.sprite.width,self.sprite.height)
        self.length = self.sprite.width


    def update(self, dt):
        physics.t += 1
        if physics.t % self.turbo_ccoldown == 0 and self.turbo_fuel < self.turbo_capacity:
            print(self.turbo_fuel)
            self.turbo_fuel += 1
        self.thrust = 0
        self.get_player_input()
        physics.move(self)
        self.sprite.x = self.position[0]
        self.sprite.y = self.position[1]
        self.sprite.rotation = -self.rotation

    def get_player_input(self):
        if self.player == 1:
            up = self.key_handler[key.UP]
            down = self.key_handler[key.DOWN]
            left = self.key_handler[key.LEFT]
            right = self.key_handler[key.RIGHT]
        else:
            up = self.key_handler[key.W]
            down = self.key_handler[key.S]
            left = self.key_handler[key.A]
            right = self.key_handler[key.D]
        if up:
            self.thrust = 1300
        elif down:
            self.thrust = -800
        if self.key_handler[key.LSHIFT] and self.turbo_fuel > 0:
            print('Vroom!')
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

