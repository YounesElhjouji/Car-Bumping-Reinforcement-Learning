from math import atan2, cos, degrees, sin, tan
import itertools
from car import Car
from entities.action import Action
from entities.car_collection import CarCollection
from entities.world import World

import numpy as np

from entities.body import Body
from utils.geometry import Geometry
from utils.sensing import SensingUtils

drag_coefficient = 0.02
friction_coefficient = 0.7
bump_back = 1
restitution = 0.9

# Move the body


def on_update(collection: CarCollection):
    World.current_time += World.dt
    check_collisions(collection)
    for car in collection.cars:
        move(car)
        refill_turbo(car.body)


def update_car(car: Car, action: Action):
    if action in [Action.NONE, Action.FORWARD, Action.BACKWARD]:
        reverse_steer(car.body)
    if action in [Action.FORWARD, Action.FORWARD_LEFT, Action.FORWARD_RIGHT]:
        go_forward(car.body)
    if action in [Action.BACKWARD, Action.BACKWARD_LEFT, Action.BACKWARD_RIGHT]:
        go_backwards(car.body)
    if action in [Action.LEFT, Action.FORWARD_LEFT, Action.BACKWARD_LEFT]:
        turn_left(car.body)
    if action in [Action.RIGHT, Action.FORWARD_RIGHT, Action.BACKWARD_RIGHT]:
        turn_right(car.body)
    move(car)


def move(car: Car):
    body = car.body
    body.max_steer = max(50 - 0.15 * body.speed, 5)
    bump_border(car)
    check_direction(body)
    if body.steer != 0:
        get_rotation(body)
    net_force = get_net_force(body)
    get_displacement(body, net_force)
    body.update_rectangles()
    car.reward_speed()


def bump_border(car: Car):
    body = car.body
    for wall in SensingUtils.get_wall_rectangles():
        is_collision, normal, depth = Geometry.are_colliding(body.car_rect, wall)
        if is_collision:
            car.punish_wall_bump()
            bump_wall(body, normal, depth)


def get_net_force(body: Body) -> np.ndarray:
    force = get_xy(body.thrust, body.rotation, 1)
    if body.speed > 0:
        # Add drag force
        drag = drag_coefficient * body.speed**2
        friction_force = body.direction * (
            drag + body.friction + abs(body.steer) * 0.05 * drag
        )
        force += get_xy(friction_force, body.rotation, -1)

        # Add sideways friction
        sideways_vector = np.array(
            [-np.sin(np.radians(body.rotation)), np.cos(np.radians(body.rotation))]
        )
        sideways_velocity = np.dot(body.velocity, sideways_vector) * sideways_vector
        side_speed = np.linalg.norm(sideways_velocity)
        if side_speed > 0:
            side_direction = sideways_velocity / side_speed
            sideways_friction = -side_direction * 0.3 * side_speed**2
            force += sideways_friction

    return force


def get_rotation(body: Body):
    turning_radius = body.width / tan(np.radians(body.steer))
    angular_velocity = body.speed / turning_radius
    rotation_diff = np.degrees(angular_velocity) * World.dt
    velocity_rotation = body.rotation + rotation_diff / 2
    body.rotation += rotation_diff
    body.rotation = body.rotation % 360
    body.velocity = get_xy(body.speed, velocity_rotation, body.direction)


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


def get_displacement(body: Body, net_force: np.ndarray):
    if body.speed < 1 and body.thrust == 0:
        body.velocity = np.array([0.0, 0.0])
    acceleration = net_force / body.mass
    body.velocity += acceleration * World.dt
    body.position = body.position + body.velocity * World.dt


# Controlling the body


def go_forward(body: Body):
    body.thrust = 1300


def go_backwards(body: Body):
    if body.speed > 10:
        body.thrust = -1300
    else:
        body.thrust = -800


def run_turbo(body: Body):
    if body.turbo_fuel > 0:
        body.turbo_fuel -= 1
        body.thrust += 10000
        body.is_turbo = True


def turn_left(body: Body):
    if body.steer < body.max_steer:
        body.steer += 100 * World.dt


def turn_right(body: Body):
    if body.steer > -body.max_steer:
        body.steer -= 100 * World.dt


def reverse_steer(body: Body):
    body.steer = 0.0


def cancel_thrust(body: Body):
    body.thrust = 0


def cancel_turbo(body: Body):
    body.is_turbo = False


def refill_turbo(body: Body):
    if (
        World.current_time - body.turbo_last_fuel > body.turbo_cooldown
        and body.turbo_fuel < body.turbo_capacity
    ):
        body.turbo_last_fuel = World.current_time
        body.turbo_fuel += 8
        body.turbo_fuel = max(body.turbo_fuel, body.turbo_capacity)


# Collision Detection


def check_collisions(collection: CarCollection):
    pairs = list(itertools.combinations(collection.cars, 2))
    for car1, car2 in pairs:
        body1, body2 = car1.body, car2.body
        is_collision, normal, depth = Geometry.are_colliding(
            body1.car_rect, body2.car_rect
        )
        if is_collision:
            bump_bodies(body1, body2, normal, depth)


def bump_bodies(body1: Body, body2: Body, normal: np.ndarray, depth: float):
    body1.position -= np.array(normal * depth / 2, dtype=np.int32)
    body2.position += np.array(normal * depth / 2, dtype=np.int32)

    apply_impulse(body1, body2, normal)


def bump_wall(body: Body, normal: np.ndarray, depth: float):
    body.position -= np.array(normal * depth / 2, dtype=np.int32)
    impulse = -(1 + restitution) * np.dot(-body.velocity, normal) * normal
    body.velocity -= impulse


def apply_impulse(body1: Body, body2: Body, normal: np.ndarray):
    rel_velocity = body2.velocity - body1.velocity
    j = -(1 + restitution) * np.dot(rel_velocity, normal)
    j /= (1 / body1.mass) + (1 / body2.mass)

    body1.velocity -= j / body1.mass * normal
    body2.velocity += j / body2.mass * normal
