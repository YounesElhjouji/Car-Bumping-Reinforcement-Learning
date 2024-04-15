from math import atan2, cos, degrees, sin, tan
from entities.world import World

import numpy as np

from entities.body import Body

world_size = (1024, 600)
drag_coefficient = 0.02
friction_coefficient = 0.7
bump_back = 0.8


def move(body: Body):
    body.max_steer = max(50 - 0.15 * body.speed, 5)
    bump_border(body)
    check_direction(body)
    if body.steer != 0:
        get_rotation(body)
    get_net_force(body)
    get_displacement(body)
    body.is_turbo = False


def bump_border(body: Body):
    if body.position[0] >= world_size[0] and body.velocity[0] > 0:
        body.velocity *= -bump_back
    elif body.position[0] <= 0 and body.velocity[0] < 0:
        body.velocity *= -bump_back
    if body.position[1] >= world_size[1] and body.velocity[1] > 0:
        body.velocity *= -bump_back
    elif body.position[1] <= 0 and body.velocity[1] < 0:
        body.velocity *= -bump_back


def bump_objects(object1, object2):
    x1, y1 = tuple(object1.position)
    x2, y2 = tuple(object2.position)
    speed = float(np.average([object1.speed, object2.speed]))

    rel_vector = np.array([x2 - x1, y2 - y1])
    new_velocity = rel_vector * speed / np.linalg.norm(rel_vector)
    object1.velocity = -new_velocity
    object2.velocity = new_velocity


def get_net_force(body: Body):
    drag = drag_coefficient * body.speed**2
    if (body.thrust > 0 and body.direction == -1) or (
        body.thrust < 0 and body.direction == 1
    ):
        body.thrust *= 2
    body.force = body.thrust
    if body.speed < 1 and body.thrust == 0:
        body.velocity = np.array([0.0, 0.0])

    elif body.speed > 0:
        body.force = body.thrust - body.direction * (
            drag + body.friction + abs(body.steer) * 0.05 * drag
        )
    body.force = get_xy(body.force, body.rotation, 1)


def get_rotation(body: Body):
    turning_radius = body.width / tan(np.radians(body.steer))
    angular_velocity = body.speed / turning_radius
    body.rotation += np.degrees(angular_velocity) * World.dt
    body.rotation = body.rotation % 360
    body.velocity = get_xy(body.speed, body.rotation, body.direction)


def get_xy(value, rotation, direction):
    theta = np.radians(rotation)
    vector_x = value * cos(theta) * direction
    vector_y = value * sin(theta) * direction
    return np.array([vector_x, vector_y])


def get_angle_difference(angleA, angleB):
    difference = abs((angleA - angleB))
    if difference > 180:
        difference = 360 - 180
    return difference


def check_direction(body: Body):
    velocity_angle = degrees(atan2(body.velocity[1], body.velocity[0]))
    body.direction = 1
    difference = get_angle_difference(velocity_angle % 360, body.rotation)
    if difference > 90:
        body.direction = -1


def get_displacement(body: Body):
    acceleration = body.force / body.mass
    body.velocity = body.velocity + acceleration * World.dt
    body.position = body.position + body.velocity * World.dt


def go_forward(body):
    body.thrust = 1300


def go_backwards(body):
    if body.speed > 10:
        body.thrust = -1300
    else:
        body.thrust = -800


def run_turbo(body):
    if body.turbo_fuel > 0:
        body.turbo_fuel -= 1
        body.thrust += 10000
        body.is_turbo = True


def turn_left(body):
    if body.steer < body.max_steer:
        body.steer += 100 * World.dt


def turn_right(body):
    if body.steer > -body.max_steer:
        body.steer -= 100 * World.dt


def reverse_steer(body):
    body.steer += 100 * World.dt if body.steer < 0 else -100 * World.dt


def cancel_thrust(body):
    body.thrust = 0
