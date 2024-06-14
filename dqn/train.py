import numpy as np
import matplotlib.pyplot as plt
from random import randint

from entities.car_collection import CarCollection
from entities.enums import Player
from entities.world import World
from game.pyglet_interface import PygletInterface, create_car
import game.physics as physics
from dqn.agent import Agent
from game.utils.pyglet import PygletUtils
from game.utils.sensing import SensingUtils
from game.utils.shaper import ShapeUtils
from game.controller import control_car


def old_():
    collection= CarCollection(cars=[create_car(position=[512, 300])])

    def on_update(dt):
        for car in collection.cars:
            car.reward = 0
            control_car(car)
        physics.on_update(collection)
        for car in collection.cars:
            car.update_sensors()
            PygletUtils.set_car_sprite_position(car)
            PygletUtils.set_fire_position(car)
            ShapeUtils.draw_debug_visuals(car=car, batch=PygletInterface.batch)
            SensingUtils.sense_walls(car, batch=PygletInterface.batch)
            SensingUtils.sense_cars(
                car=car, car_collection=collection, batch=PygletInterface.batch
            )
            PygletUtils.draw_sensors(car=car, batch=PygletInterface.batch)
        # SensingUtils.debug_line_intersection(batch=PygletInterface.batch)

    PygletInterface.start_(on_update=on_update)


def train():
    cars = []
    archs = [
        [8, 64, 9],
        [8, 128, 9],
    ]
    scores = []
    gen = 0
    for arch in archs:
        cars.append(
            create_car(
                position=[
                    randint(20, World.size[0] - 20),
                    randint(20, World.size[1] - 20),
                ],
                rotation=randint(0, 359),
                player=Player.AI,
                agent=Agent(arch),
            )
        )

    # Initialize the plot
    fig, ax = plt.subplots()
    car_scores = {car.id_: [] for car in cars}
    car_lines = {
        car.id_: ax.plot(
            [],
            [],
            label=f"{car.agent.model.arch}",
        )[0]
        for car in cars
    }
    ax.legend()

    def update_plot():
        for car in cars:
            car_lines[car.id_].set_data(
                range(len(car_scores[car.id_])), car_scores[car.id_]
            )
        ax.relim()
        ax.set_ylim(
            -50,
            max(10, max((max(scores) for scores in car_scores.values()), default=10)),
        )
        ax.autoscale_view()
        plt.draw()
        plt.pause(0.001)

    def on_update(dt):
        nonlocal gen, scores
        World.current_time += dt

        if World.current_time > 20:
            gen += 1
            print(f"Generation {gen}")
            scores.append(int(np.mean([car.score for car in cars])))
            for car in cars:
                car_scores[car.id_].append(car.score)
            update_plot()
            for car in cars:
                agent = car.agent
                agent.n_games += 1
                agent.train_batch()
                agent.update_target_network()
                car.score = 0
            print(f"Average scores: {scores}")
            World.current_time = 0
            for car in cars:
                car.body.position = [
                    randint(20, World.size[0] - 20),
                    randint(20, World.size[1] - 20),
                ]
                car.body.rotation = randint(0, 360)

        for car in cars:
            car.reward = 0
            agent = car.agent
            state = car.get_state()
            action = agent.get_action(state)

            physics.update_car(car, action)

            car.update_sensors()
            PygletUtils.set_car_sprite_position(car)
            SensingUtils.sense_walls(car, batch=PygletInterface.batch)
            car.update_score()

            state_new = car.get_state()
            reward = car.reward
            agent.train_step(
                state0=state, state1=state_new, reward=reward, action=action, done=False
            )

    PygletInterface.start_(on_update=on_update)


if __name__ == "__main__":
    train()
