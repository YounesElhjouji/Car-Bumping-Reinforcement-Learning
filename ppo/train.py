import argparse
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
MODELS_PATH = join(os.getcwd(), "models")
HIGH_SCORES = {}


architectures = [
    [64, 64],
    [128, 128, 64],
    [256, 128, 64],
    [128, 128],
    [256, 256],
    [32, 32],
    [64],
    [32, 32, 32],
    [128, 64, 32],
]


def initialize_cars(num_cars):
    cars = []

    for i in range(num_cars):
        arch = architectures[i % len(architectures)]
        agent = PPOAgent(input_dim=18, action_dim=5, hidden_layers=arch)
        policy_path = join(MODELS_PATH, f"{arch}-policy.pth")
        value_path = join(MODELS_PATH, f"{arch}-value.pth")
        try:
            agent.load_models(policy_path, value_path)
        except FileNotFoundError:
            print(
                f"Warning: Model files {policy_path} and {value_path} not found. Using initialized models."
            )

        dist = 40
        car = create_car(
            position=[
                randint(dist, World.size[0] - dist),
                randint(dist, World.size[1] - dist),
            ],
            rotation=randint(0, 359),
            player=Player.AI,
            agent=agent,
        )
        HIGH_SCORES[car.id_] = float("-inf")
        cars.append(car)
    return cars


def handle_exit_state(car: Car, memory: Memory):
    assert isinstance(car.agent, PPOAgent)
    lifetime = World.current_time - car.last_reset
    print(
        f"Car {str(car.id_)[-4:]}, Arch: {car.agent.hidden_layers}, Score/min: {(car.score/lifetime)*60}"
    )
    save_best_scored_model(car)  # save_best_scored_model(car)
    car.agent.update(memory)
    memory.clear_memory()
    car.reset()


def save_best_scored_model(car: Car):
    assert isinstance(car.agent, PPOAgent)
    if car.score >= HIGH_SCORES[car.id_]:
        HIGH_SCORES[car.id_] = car.score
        arch = car.agent.policy.hidden_layers
        policy_path = join(MODELS_PATH, f"{arch}-policy.pth")
        value_path = join(MODELS_PATH, f"{arch}-value.pth")
        car.agent.save_models(policy_path, value_path)


def reset_world(cars):
    World.current_time = 0
    for car in cars:
        car.reset()


def action_to_multiaction(action_probs):
    action_probs = action_probs > 0.0  # Convert probabilities to binary actions
    return MultiAction.from_list(action_probs.tolist())


def update_car_state(car: Car, memory: Memory):
    assert isinstance(car.agent, PPOAgent)
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
    reward = car.reward

    # Save in memory
    memory.states.append(torch.FloatTensor(state))
    memory.actions.append(torch.FloatTensor(action))
    memory.action_probs.append(action_logprobs)
    memory.rewards.append(reward)
    memory.is_terminals.append(car.touches_wall)


def train(is_visual: bool):
    num_cars = 10  # Set the number of cars
    cars: list[Car] = initialize_cars(num_cars)
    memories = [Memory() for _ in range(num_cars)]

    def on_update(dt):
        World.current_time += dt
        for car, memory in zip(cars, memories):
            update_car_state(car, memory)
            lifetime = World.current_time - car.last_reset
            if (car.touches_wall and len(memory.rewards) > 10) or lifetime > 10:
                handle_exit_state(car, memory)

    if is_visual:
        PygletInterface.start_(on_update=on_update)
    else:
        while True:
            on_update(dt=World.dt)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train AI cars with PPO.")
    parser.add_argument(
        "--is-visual",
        action="store_true",
        help="Run the training with visualization. Default is False.",
    )
    args = parser.parse_args()

    train(args.is_visual)
