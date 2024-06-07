import numpy as np
import matplotlib.pyplot as plt
from random import randint

from entities.car_collection import CarCollection
from entities.enums import Player
from entities.world import World
from interfaces.pyglet_interface import PygletInterface, create_car
import physics
from pytorch.agent import Agent
from utils.pyglet import PygletUtils
from utils.sensing import SensingUtils
from utils.shaper import ShapeUtils
from controller import control_car


def add_cars() -> CarCollection:
    cars = []
    cars.append(create_car(position=[512, 300]))
    # cars.append(create_car(position=[700, 300], rotation=90, player=Player.P2))
    # for _ in range(15):
    #     cars.append(
    #         create_car(
    #             position=[
    #                 randint(20, World.size[0] - 20),
    #                 randint(20, World.size[1] - 20),
    #             ],
    #             rotation=randint(0, 359),
    #             player=Player.RANDOM,
    #         )
    #     )
    return CarCollection(cars=cars)


def old_game():
    collection = add_cars()

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

    PygletInterface.start_game(on_update=on_update)


def train():
    cars = []
    archs = [
        [8, 16, 9],
        [8, 32, 9],
        [8, 64, 9],
        [8, 128, 9],
        [8, 256, 9],
        [8, 512, 9],
        [8, 128, 32, 9],
        [8, 9],
    ]
    scores = []
    gen = 0
    batch_ids = []
    for arch in archs:
        for i in range(2):
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
            if i == 0:
                batch_ids.append(cars[-1].id_)

    # cars.append(create_car(position=[512, 300], agent=Agent([8, 8, 9])))

    # Initialize the plot
    fig, ax = plt.subplots()
    car_scores = {car.id_: [] for car in cars}
    car_lines = {
        car.id_: ax.plot(
            [],
            [],
            label=f"{car.agent.model.arch} {'nob' if car.id_ not in batch_ids else ''}",
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
                if car.id_ in batch_ids:
                    agent.train_batch()

                agent.update_target_network()
                update_plot()
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

    PygletInterface.start_game(on_update=on_update)


if __name__ == "__main__":
    train()
