from math import atan2, cos, degrees, sin, tan
import itertools
from entities.car_collection import CarCollection
from entities.world import World

import numpy as np

from entities.body import Body
from utils.trigonometry import TrigUtils

drag_coefficient = 0.02
friction_coefficient = 0.7
bump_back = 1

# Move the body


def on_update(dt, collection: CarCollection):
    World.current_time += dt
    check_collisions(collection)
    for car in collection.cars:
        move(car.body)
        refill_turbo(car.body)


def move(body: Body):
    body.max_steer = max(50 - 0.15 * body.speed, 5)
    bump_border(body)
    check_direction(body)
    if body.steer != 0:
        get_rotation(body)
    net_force = get_net_force(body)
    get_displacement(body, net_force)
    body.update_rectangles()


def bump_border(body: Body):
    for point in body.car_rect.points:
        is_bump = bump_corner(body, point)
        if is_bump:
            return


def bump_corner(body: Body, point: np.ndarray) -> bool:
    if point[0] >= World.size[0]:
        bump_wall(body, np.array([1.0, 0.0]))
        return True
    if point[0] <= 0:
        bump_wall(body, np.array([-1.0, 0.0]))
        return True
    if point[1] >= World.size[1]:
        bump_wall(body, np.array([0.0, 1.0]))
        return True
    if point[1] <= 0:
        bump_wall(body, np.array([0.0, -1.0]))
        return True
    return False


def get_net_force(body: Body) -> np.ndarray:
    # break when thrusting in direction opposite to movement
    if (body.thrust > 0 and body.direction == -1) or (
        body.thrust < 0 and body.direction == 1
    ):
        body.thrust *= 2

    force = get_xy(body.thrust, body.rotation, 1)

    if body.speed > 0:
        drag = drag_coefficient * body.speed**2
        friction_force = body.direction * (
            drag + body.friction + abs(body.steer) * 0.05 * drag
        )
        force += get_xy(friction_force, body.rotation, -1)

        sideways_vector = np.array(
            [-np.sin(np.radians(body.rotation)), np.cos(np.radians(body.rotation))]
        )
        sideways_velocity = np.dot(body.velocity, sideways_vector) * sideways_vector
        side_speed = np.linalg.norm(sideways_velocity)

        if side_speed > 0:
            side_direction = sideways_velocity / side_speed
            sideways_friction = -side_direction * 0.3 * side_speed**2
            force += sideways_friction

    if np.linalg.norm(body.collision_force) > 0:
        force += body.collision_force

    return force


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


def get_displacement(body: Body, net_force: np.ndarray):
    if body.speed < 1 and body.thrust == 0:
        body.velocity = np.array([0.0, 0.0])
    acceleration = net_force / body.mass
    body.velocity = body.velocity + acceleration * World.dt
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
    body.steer += 100 * World.dt if body.steer < 0 else -100 * World.dt


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
    for car in collection.cars:
        car.body.collision_force *= 0.1
    pairs = list(itertools.combinations(collection.cars, 2))
    for car1, car2 in pairs:
        body1, body2 = car1.body, car2.body
        if TrigUtils.are_colliding(body1.car_rect, body2.car_rect):
            bump_bodies(body1, body2)


def bump_bodies(body1: Body, body2: Body):
    rel_vector = body2.car_rect.center - body1.car_rect.center
    rel_direction = rel_vector / np.linalg.norm(rel_vector)
    rel_velocity = body2.velocity - body1.velocity
    collision_force = float(
        5 * (body1.mass + body2.mass) * np.linalg.norm(rel_velocity)
    )

    # Remove the component of the velocity that is directed towards the other body
    body1.velocity -= max(0, np.dot(body1.velocity, rel_direction)) * rel_direction
    body2.velocity -= max(0, np.dot(body2.velocity, -rel_direction)) * -rel_direction

    set_collision_force(body1, collision_force, rel_direction, sign=-1)
    set_collision_force(body2, collision_force, rel_direction, sign=1)


def bump_wall(body: Body, rel_direction: np.ndarray):
    collision_force = 80 * body.mass * body.speed
    body.velocity -= max(0, np.dot(body.velocity, rel_direction)) * rel_direction
    body.thrust = 0
    set_collision_force(body, collision_force, rel_direction, sign=-1)


def set_collision_force(
    body: Body, collision_force: float, rel_direction: np.ndarray, sign: int
):
    collision_force = max(collision_force, 100)
    body.collision_force += sign * collision_force * rel_direction
