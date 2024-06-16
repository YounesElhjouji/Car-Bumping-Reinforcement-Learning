import matplotlib.pyplot as plt
from random import randint
import torch
import os
from os.path import join

from entities.enums import Player
from entities.world import World
from game.car import Car
from game.pyglet_interface import PygletInterface, create_car
import game.physics as physics
from ppo.agent import PPOAgent, Memory  # Importing PPO agent and Memory
from game.utils.pyglet import PygletUtils
from game.utils.sensing import SensingUtils
from entities.action import (
    MultiAction,
)  # Assuming this file contains your MultiAction and OneHotAction classes

GENERATION = 0
MODELS_PATH = join(os.getcwd(), 'models')


def initialize_cars(num_cars):
    cars = []

    for _ in range(num_cars):
        agent = PPOAgent(
            input_dim=14, action_dim=5
        )  # Adjust input_dim to 8 and action_dim to 5
        agent.load_models(
            join(MODELS_PATH, "policy.pth"), join(MODELS_PATH, "value.pth")
        )
        car = create_car(
            position=[randint(20, World.size[0] - 20), randint(20, World.size[1] - 20)],
            rotation=randint(0, 359),
            player=Player.AI,
            agent=agent,
        )
        cars.append(car)
    return cars


def setup_plot(cars):
    fig, ax = plt.subplots()
    car_lines = {car.id_: ax.plot([], [], label=f"Car {i}")[0] for i, car in enumerate(cars)}
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


def handle_generation_end(cars, car_scores, ax, car_lines, memories):
    global GENERATION
    GENERATION += 1
    World.current_time = 0
    print(f"Generation {GENERATION}")
    for car in cars:
        car_scores[car.id_].append(car.score)
    update_plot(ax, car_scores, car_lines)
    save_best_scored_model(cars)
    for car, memory in zip(cars, memories):
        car.agent.update(memory)
        memory.clear_memory()
        car.score = 0


def save_best_scored_model(cars: list[Car]):
    best_car = max(cars, key=lambda car: car.score)
    best_car.agent.save_models(
        join(MODELS_PATH, f"policy.pth"),
        join(MODELS_PATH, f"value.pth"),
    )

def reset_world(cars):
    World.current_time = 0
    for car in cars:
        car.body.position = [
            randint(20, World.size[0] - 20),
            randint(20, World.size[1] - 20),
        ]
        car.body.rotation = randint(0, 360)
        car.body.reset_physics()


def action_to_multiaction(action_probs):
    action_probs = action_probs > 0.5  # Convert probabilities to binary actions
    return MultiAction.from_list(action_probs.tolist())


def update_car_state(car, memory):
    car.reward = 0
    agent = car.agent
    state = car.get_state().to_list()  # Convert state to list
    action, action_logprobs = agent.select_action(
        state
    )  # Get action and log probabilities
    action_entity = action_to_multiaction(action)  # Convert to MultiAction
    physics.update_car(car, action_entity)
    car.update_sensors()
    PygletUtils.set_car_sprite_position(car)
    PygletUtils.set_fire_position(car)
    SensingUtils.sense_walls(car, batch=PygletInterface.batch)
    state_new = car.get_state().to_list()  # Convert state to list
    reward = car.reward

    # Save in memory
    memory.states.append(torch.FloatTensor(state))
    memory.actions.append(torch.FloatTensor(action))
    memory.action_probs.append(action_logprobs)
    memory.rewards.append(reward)
    memory.is_terminals.append(False)

    # Update the car's score
    car.update_score()


def train():
    num_cars = 3  # Set the number of cars
    cars = initialize_cars(num_cars)
    memories = [Memory() for _ in range(num_cars)]
    fig, ax, car_lines = setup_plot(cars)
    car_scores = {car.id_: [] for car in cars}

    def on_update(dt):
        World.current_time += dt
        if World.current_time > 5:
            handle_generation_end(cars, car_scores, ax, car_lines, memories)
            reset_world(cars)

        for car, memory in zip(cars, memories):
            update_car_state(car, memory)

    PygletInterface.start_(on_update=on_update)


if __name__ == "__main__":
    train()
