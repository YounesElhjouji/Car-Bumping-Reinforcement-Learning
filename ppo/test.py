import argparse
from random import randint
import os
from os.path import join

from entities.enums import Player
from entities.world import World
from game.car import Car
from game.pyglet_interface import PygletInterface, create_car
import game.physics as physics
from ppo.agent import PPOAgent  # Importing PPO agent and Memory
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
    [16, 16, 16],
    [32, 16],
    [16, 16],
    [32, 32],
    [16],
    [32, 32, 32],
    [32, 64, 32],
]


def initialize_cars():
    cars = []
    dist = 40
    position = [
        randint(dist, World.size[0] - dist),
        randint(dist, World.size[1] - dist),
    ]
    rotation = randint(0, 359)
    for i in range(len(architectures)):
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

        car = create_car(
            position=position,
            rotation=rotation,
            player=Player.AI,
            agent=agent,
        )
        HIGH_SCORES[car.id_] = float("-inf")
        cars.append(car)
    return cars


def action_to_multiaction(action_probs):
    action_probs = action_probs > 0.0  # Convert probabilities to binary actions
    return MultiAction.from_list(action_probs.tolist())


def update_car_state(car: Car):
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


def show_scores(cars: list[Car]):
    cars.sort(key=lambda car: car.score)
    output = ""
    for car in cars:
        output += f"Car {car.agent.hidden_layers}; Score: {car.score}\n"
    print(output)
    with open(join(MODELS_PATH, "test_results.txt"), "w") as f:
        f.write(output)


def test(is_visual: bool):
    cars: list[Car] = initialize_cars()
    is_running = True

    def on_update(dt):
        nonlocal is_running
        World.current_time += dt
        for car in cars:
            update_car_state(car)
        if World.current_time > 60:
            show_scores(cars)
            PygletInterface.end_()
            is_running = False

    if is_visual:
        PygletInterface.start_(on_update=on_update)
    else:
        while is_running:
            on_update(dt=World.dt)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train AI cars with PPO.")
    parser.add_argument(
        "--is-visual",
        action="store_true",
        help="Run the training with visualization. Default is False.",
    )
    args = parser.parse_args()

    test(args.is_visual)
