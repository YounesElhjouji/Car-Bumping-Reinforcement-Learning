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
        [14, 16, 9],
        [14, 32, 9],
        [14, 128, 9],
        [14, 64, 64, 9],
        [14, 64, 64, 64, 9],
        [14, 16, 16, 9],
        [14, 8, 8, 8, 9],
        [14, 8, 8, 9],
    ]

    for arch in archs:
        for _ in range(2):
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

    def on_update(dt):
        World.current_time += dt

        if World.current_time > 60:
            print("minute has passed, long training ... ")
            for car in cars:
                agent = car.agent
                agent.train_batch()
                print(f"Score: {car.score}, Arch: {car.agent.model.arch}")
                car.score = 0
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
