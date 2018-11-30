import math
from math import cos,sin,tan
import numpy as np
dt = 0.01


def move(object):

    if object.steer != 0:
        get_rotation(object)

    force = get_xy(object.force, object.rotation)
    get_displacement(object, force)



def get_rotation(object):
    speed = np.linalg.norm(object.velocity)
    turning_radius = object.length / tan(np.radians(object.steer))
    angular_velocity = speed / turning_radius
    object.rotation += np.degrees(angular_velocity) * dt
    object.rotation = object.rotation % 360
    object.velocity = get_xy(speed, object.rotation)

def get_xy(value, rotation):
    theta = np.radians(rotation)
    vector_x = value*cos(theta)
    vector_y = value*sin(theta)
    return np.array([vector_x, vector_y])


def check_speed(velocity):
    speed = np.linalg.norm(velocity)
    ratio = speed / 200
    if ratio > 1:
        velocity = velocity/ratio
    return velocity


def get_displacement(object,force):
    acceleration = force / object.mass
    object.velocity = object.velocity + acceleration * dt
    object.velocity = check_speed(object.velocity)
    object.position = object.position + object.velocity * dt #+ 0.5 * acceleration * math.pow(dt, 2)
