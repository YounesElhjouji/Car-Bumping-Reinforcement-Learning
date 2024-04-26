from entities.car_collection import CarCollection
from entities.enums import Player
from interfaces.pyglet_interface import PygletInterface, create_car
import physics
from utils.pyglet import PygletUtils
from utils.sensing import SensingUtils
from utils.shaper import ShapeUtils
from controller import control_car


def add_cars() -> CarCollection:
    cars = []
    cars.append(create_car(position=[512, 300]))
    cars.append(create_car(position=[700, 300], rotation=90, player=Player.P2))
    # for _ in range(31):
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


if __name__ == "__main__":
    collection = add_cars()

    def on_update(dt):
        for car in collection.cars:
            control_car(car)
        physics.on_update(dt, collection)
        for car in collection.cars:
            car.update_sensors()
            PygletUtils.set_car_sprite_position(car)
            PygletUtils.set_fire_position(car)
            ShapeUtils.draw_debug_visuals(car=car, batch=PygletInterface.batch)
            SensingUtils.sense_walls(car, batch=PygletInterface.batch)
            PygletUtils.draw_sensors(car=car, batch=PygletInterface.batch)

    PygletInterface.start_game(on_update=on_update)
