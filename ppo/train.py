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
HIGH_SCORE = -1000

# Example architectures to test
architectures = [
    [64, 64],
    [128, 128, 64],
    [256, 128, 64],
    [128, 128],
    [256, 256],
    [32, 32],
    [64],
    [32, 32, 32],
    [128, 64, 32]
]


def initialize_cars(num_cars):
    cars = []

    for i in range(num_cars):
        arch = architectures[i % len(architectures)]
        agent = PPOAgent(
            input_dim=18, action_dim=5, hidden_layers=arch
        )
        policy_path = join(MODELS_PATH, f"{arch}-policy.pth")
        value_path = join(MODELS_PATH, f"{arch}-value.pth")
        try:
            agent.load_models(policy_path, value_path)
        except FileNotFoundError:
            print(f"Warning: Model files {policy_path} and {value_path} not found. Using initialized models.")

        dist = 20
        car = create_car(
            position=[randint(dist, World.size[0] - dist), randint(dist, World.size[1] - dist)],
            rotation=randint(0, 359),
            player=Player.AI,
            agent=agent,
        )
        cars.append(car)
    return cars


def setup_plot(cars):
    fig, ax = plt.subplots()
    car_lines = {car.id_: ax.plot([], [], label=f"Car {i} {car.agent.hidden_layers}")[0] for i, car in enumerate(cars)}
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
    global HIGH_SCORE
    best_car = max(cars, key=lambda car: car.score)
    if best_car.score > HIGH_SCORE:
        HIGH_SCORE = best_car.score
        arch = best_car.agent.policy.hidden_layers
        policy_path = join(MODELS_PATH, f"{arch}-policy.pth")
        value_path = join(MODELS_PATH, f"{arch}-value.pth")
        best_car.agent.save_models(policy_path, value_path)


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
    action_probs = action_probs > 0.0  # Convert probabilities to binary actions
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
    num_cars = 10  # Set the number of cars
    cars = initialize_cars(num_cars)
    memories = [Memory() for _ in range(num_cars)]
    fig, ax, car_lines = setup_plot(cars)
    car_scores = {car.id_: [] for car in cars}

    def on_update(dt):
        World.current_time += dt
        if World.current_time > 3:
            handle_generation_end(cars, car_scores, ax, car_lines, memories)
            reset_world(cars)

        for car, memory in zip(cars, memories):
            update_car_state(car, memory)

    PygletInterface.start_(on_update=on_update)


if __name__ == "__main__":
    train()
