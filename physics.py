import math
from math import cos,sin,tan
import numpy as np
t = 0
dt = 0.01
world_size = (1024, 600)
drag_coefficient = 0.02
friction_coefficient = 0.7
bump_back = 0.8


def move(thing):
    thing.speed = np.linalg.norm(thing.velocity)
    thing.max_steer = 47 - 0.1 * thing.speed
    bump(thing)
    check_direction(thing)
    if thing.steer != 0:
        get_rotation(thing)
    get_net_force(thing)
    get_displacement(thing)


def bump(thing):
    if thing.position[0] >= world_size[0] and thing.velocity[0] > 0:
        thing.velocity *= -bump_back
    elif thing.position[0] <= 0 and thing.velocity[0] < 0:
        thing.velocity *= -bump_back
    if thing.position[1] >= world_size[1] and thing.velocity[1] > 0:
        thing.velocity *= -bump_back
    elif thing.position[1] <= 0 and thing.velocity[1] < 0:
        thing.velocity *= -bump_back


def get_net_force(thing):
    drag = drag_coefficient * thing.speed**2
    if (thing.thrust > 0 and thing.direction == -1) or (thing.thrust < 0 and thing.direction == 1):
        thing.thrust *= 2
    thing.force = thing.thrust
    if thing.speed < 1 and thing.thrust == 0:
        thing.velocity = np.array([0.0, 0.0])
    elif thing.speed > 0:
        thing.force = thing.thrust - thing.direction * (drag + thing.friction)
    thing.force = get_xy(thing.force, thing.rotation, 1)


def get_rotation(thing):
    turning_radius = thing.length / tan(np.radians(thing.steer))
    angular_velocity = thing.speed / turning_radius
    thing.rotation += np.degrees(angular_velocity) * dt
    thing.rotation = thing.rotation % 360
    thing.velocity = get_xy(thing.speed, thing.rotation, thing.direction)


def get_xy(value, rotation, direction):
    theta = np.radians(rotation)
    vector_x = value*cos(theta) * direction
    vector_y = value*sin(theta) * direction
    return np.array([vector_x, vector_y])


def get_angle_difference(angleA, angleB):
    difference = abs((angleA - angleB))
    if difference > 180:
        difference = 360-180
    return difference


def check_direction(thing):
    velocity_angle = math.degrees(math.atan2(thing.velocity[1], thing.velocity[0]))
    thing.direction = 1
    difference = get_angle_difference(velocity_angle % 360, thing.rotation)
    if difference > 90:
        thing.direction = -1


def get_displacement(thing):
    acceleration = thing.force / thing.mass
    thing.velocity = thing.velocity + acceleration * dt
    thing.position = thing.position + thing.velocity * dt




