import math
from math import cos,sin,tan
import numpy as np
dt = 0.01


def move(thing):

    if thing.steer != 0:
        get_rotation(thing)

    force = get_xy(thing.force, thing.rotation, 1)
    get_displacement(thing, force)



def get_rotation(thing):
    speed = np.linalg.norm(thing.velocity)
    turning_radius = thing.length / tan(np.radians(thing.steer))
    angular_velocity = speed / turning_radius
    thing.rotation += np.degrees(angular_velocity) * dt
    thing.rotation = thing.rotation % 360
    thing.velocity = get_xy(speed, thing.rotation, thing.direction)

def get_xy(value, rotation, direction):
    theta = np.radians(rotation)
    vector_x = value*cos(theta) * direction
    vector_y = value*sin(theta) * direction
    return np.array([vector_x, vector_y])


def check_speed(velocity):
    speed = np.linalg.norm(velocity)
    ratio = speed / 200
    if ratio > 1:
        velocity = velocity/ratio
    return velocity

def get_angle_difference(angleA, angleB):
    difference = abs((angleA - angleB))
    if difference > 180:
        difference = 360-180
    return difference

def get_displacement(thing, force):
    acceleration = force / thing.mass
    thing.velocity = thing.velocity + acceleration * dt
    thing.velocity = check_speed(thing.velocity)
    velocity_angle = math.degrees(math.atan2(thing.velocity[1],thing.velocity[0]))
    thing.direction = 1
    difference = get_angle_difference(velocity_angle % 360,thing.rotation)
    print(difference)
    if difference > 90:
        thing.direction = -1
    thing.position = thing.position + thing.velocity * dt




