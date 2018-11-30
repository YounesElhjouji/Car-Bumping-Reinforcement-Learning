import pyglet
from pyglet.window import key
import numpy as np
import physics
import math


class Car(object):
    def __init__(self, handler, position=[50, 100],rotation=0, player=1,image = 'car'):
        self.key_handler = handler
        self.player = player
        self.rotate = 25
        self.force = 0
        self.position = np.array(position)
        self.velocity = np.array([0.0, 0.0])
        self.steer = 0
        self.mass = 10
        self.direction = 1

        image = pyglet.resource.image(image+'.png')
        car_sprite = pyglet.sprite.Sprite(image, self.position[0], self.position[1])
        car_sprite.image.anchor_x = car_sprite.image.width / 2
        car_sprite.image.anchor_y = car_sprite.image.height / 2
        car_sprite.rotation = rotation
        car_sprite.scale = 1

        self.sprite = car_sprite
        self.rotation = self.sprite.rotation
        self.length = self.sprite.width


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
            self.force = 1000
        elif down:
            self.force = -1000
        if left:
            if self.steer < 25:
                self.steer += 1
        elif right:
            if self.steer > -25:
                self.steer -= 1
        else:
            if self.steer > 0:
                self.steer -= 1
            elif self.steer < 0:
                self.steer += 1



    def update(self, dt):
        self.force = 0
        #self.steer = 0
        self.get_player_input()
        physics.move(self)
        self.sprite.x = self.position[0]
        self.sprite.y = self.position[1]
        #self.rotation += 10
        self.sprite.rotation = -self.rotation

        #   Prints
        #print(self.sprite.rotation, " rads ", math.radians(self.sprite.rotation))

