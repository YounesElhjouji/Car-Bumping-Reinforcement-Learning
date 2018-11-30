import math
from math import cos,sin,tan
import numpy as np
dt = 0.01


def move(car):
    speed = np.linalg.norm(car.velocity)
    if car.steer != 0:
        car.rotation, car.velocity = get_rotation(car.rotation, car.velocity, car.steer, car.length)

    force = get_xy(car.force, car.rotation)
    car.position, car.velocity = get_displacement(car.position, car.velocity, force, car.mass)



def get_rotation(rotation, velocity, steer, length):
    speed = np.linalg.norm(velocity)
    turning_radius = length / tan(np.radians(steer))
    angular_velocity = speed / turning_radius
    rotation += np.degrees(angular_velocity) * dt
    rotation = rotation % 360
    velocity_rotation = np.degrees(math.atan(velocity[1] / velocity[0])) % 360
    difference = get_angle_difference(velocity_rotation,rotation)
    velocity = get_xy(speed, rotation)
    return rotation, velocity


def get_angle_difference(angleA, angleB):
    difference = abs((angleA - angleB))
    if difference > 180:
        difference = 360-180
    return difference


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


def get_displacement(position, velocity, force, mass):
    acceleration = force / mass
    new_velocity = velocity + acceleration * dt
    new_velocity = check_speed(new_velocity)
    new_position = position + new_velocity * dt #+ 0.5 * acceleration * math.pow(dt, 2)
    return new_position, new_velocity
