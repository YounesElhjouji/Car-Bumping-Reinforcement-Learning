import numpy as np
import matplotlib.pyplot as plt
from random import randint

from entities.enums import Player
from entities.world import World
from game.pyglet_interface import PygletInterface, create_car
import game.physics as physics
from dqn.agent import QNetAgent
from game.utils.pyglet import PygletUtils
from game.utils.sensing import SensingUtils

GENERATION = 0

def initialize_cars(archs):
    cars = []
    for arch in archs:
        car = create_car(
            position=[randint(20, World.size[0] - 20), randint(20, World.size[1] - 20)],
            rotation=randint(0, 359),
            player=Player.AI,
            agent=QNetAgent(arch)
        )
        cars.append(car)
    return cars


def setup_plot(cars):
    fig, ax = plt.subplots()
    car_lines = {
        car.id_: ax.plot([], [], label=f"{car.agent.model.arch}")[0] for car in cars
    }
    ax.legend()
    return fig, ax, car_lines


def update_plot(ax, car_scores, car_lines):
    for car_id, line in car_lines.items():
        line.set_data(range(len(car_scores[car_id])), car_scores[car_id])
    ax.relim()
    max_score = max((max(scores) for scores in car_scores.values()), default=10)
    ax.set_ylim(-50, max(10, max_score))
    ax.autoscale_view()
    plt.draw()
    plt.pause(0.001)


def on_update(dt, cars, car_scores, car_lines, ax):
    World.current_time += dt

    if World.current_time > 20:
        handle_generation_end(cars, car_scores, ax, car_lines)
        reset_world(cars)

    for car in cars:
        update_car_state(car)
        car.update_score()



def handle_generation_end(cars, car_scores, ax, car_lines):
    global GENERATION
    GENERATION += 1
    print(f"Generation {GENERATION}")
    for car in cars:
        car_scores[car.id_].append(car.score)
    update_plot(ax, car_scores, car_lines)
    for car in cars:
        car.agent.train_batch()
        car.agent.update_target_network()
        car.score = 0


def reset_world(cars):
    World.current_time = 0
    for car in cars:
        car.body.position = [randint(20, World.size[0] - 20), randint(20, World.size[1] - 20)]
        car.body.rotation = randint(0, 360)


def update_car_state(car):
    car.reward = 0
    agent = car.agent
    state = car.get_state()
    action = agent.get_action(state)
    physics.update_car(car, action)
    car.update_sensors()
    PygletUtils.set_car_sprite_position(car)
    SensingUtils.sense_walls(car, batch=PygletInterface.batch)
    state_new = car.get_state()
    reward = car.reward
    agent.train_step(state0=state, state1=state_new, reward=reward, action=action, done=False)


def train():
    archs = [[18, 64, 9], [18, 128, 9]]
    cars = initialize_cars(archs)
    fig, ax, car_lines = setup_plot(cars)
    car_scores = {car.id_: [] for car in cars}

    PygletInterface.start_(on_update=lambda dt: on_update(dt, cars, car_scores, car_lines, ax))


if __name__ == "__main__":
    train()
