import itertools
from game.car import Car


class CarCollection:
    def __init__(self, cars: list[Car]) -> None:
        self.cars = cars
        self.pairs = itertools.combinations(cars, 2)

    # def add_car(
    #     self, position: list[int], rotation: int = 0, player: Player = Player.P1
    # ) -> None:
    #     batch = PygletInterface.batch
    #     car_sprite = PygletUtils.create_car_sprite(width=World.car_width, batch=batch)
    #     fire_sprite = PygletUtils.create_fire_sprite(
    #         car_height=car_sprite.height, batch=batch
    #     )
    #
    #     return Car(
    #         position=np.array(position),
    #         rotation=rotation,
    #         car_sprite=car_sprite,
    #         fire_sprite=fire_sprite,
    #         player=player,
    #     )
