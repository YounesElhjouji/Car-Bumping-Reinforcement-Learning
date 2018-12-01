import pyglet
from pyglet.window import key
import numpy as np
import physics
from physics import dt, friction_coefficient, t
import math


class Car(object):
    def __init__(self, handler, position=[50, 100],rotation=0, player=1, car_sprite=[], fire_sprite = []):
        self.turbo_capacity = 40
        self.turbo_ccoldown = 50
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
        self.fire = fire_sprite
        self.sprite = car_sprite
        self.length = self.sprite.width
        self.sprite.x = self.position[0]
        self.sprite.y = self.position[1]
        self.sprite.rotation = rotation
        self.rotation = self.sprite.rotation


    def update(self, dt):
        physics.t += 1
        if physics.t % self.turbo_ccoldown == 0 and self.turbo_fuel < self.turbo_capacity:
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

