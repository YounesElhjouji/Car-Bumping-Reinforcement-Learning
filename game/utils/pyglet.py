from pyglet.graphics import Batch
from math import sin, cos, radians
from pyglet.resource import Loader
from pyglet.sprite import Sprite

from game.car import Car
from game.utils.shaper import ShapeUtils


class PygletUtils:
    @staticmethod
    def create_car_sprite(width: int, batch: Batch) -> Sprite:
        my_image = Loader(path="../resources").image(name="car1.png")
        car_sprite: Sprite = Sprite(img=my_image, batch=batch)
        car_sprite.scale = width / car_sprite.width
        car_sprite.image.anchor_x = car_sprite.width // 2
        car_sprite.image.anchor_y = car_sprite.height // 2
        return car_sprite

    @staticmethod
    def create_fire_sprite(car_height: int, batch: Batch) -> Sprite:
        my_image = Loader(path="../resources").image(name="fire.png")
        fire_sprite = Sprite(my_image, batch=batch)
        fire_sprite.anchor_x = fire_sprite.width
        fire_sprite.anchor_y = fire_sprite.height // 2
        fire_sprite.scale = 0.6 * car_height / fire_sprite.height
        fire_sprite.visible = False
        return fire_sprite

    @staticmethod
    def set_car_sprite_position(car: Car):
        car.car_sprite.x = car.body.position[0]
        car.car_sprite.y = car.body.position[1]
        car.car_sprite.rotation = -car.body.rotation

    @staticmethod
    def set_fire_position(car: Car):
        """
        Position fire sprite relative to car sprite if turbo is on
        """
        offset_h = -1.05
        offset_v = -0.3
        car.fire_sprite.visible = car.body.is_turbo
        if not car.body.is_turbo:
            return
        car.fire_sprite.rotation = car.car_sprite.rotation
        car.fire_sprite.x = (
            car.car_sprite.x
            + offset_h * car.fire_sprite.width * cos(radians(car.body.rotation))
            + offset_v * car.fire_sprite.height * sin(radians(car.body.rotation))
        )
        car.fire_sprite.y = (
            car.car_sprite.y
            + offset_h * car.fire_sprite.width * sin(radians(car.body.rotation))
            - offset_v * car.fire_sprite.height * cos(radians(car.body.rotation))
        )

    @staticmethod
    def draw_sensors(car: Car, batch: Batch):
        # Calculate the end point of the line
        car.metadata["sensors"] = {}
        for sensor in car.wall_sensors + car.car_sensors:
            start_x, start_y = sensor.position[0], sensor.position[1]
            rotation = sensor.rotation
            end_x = start_x + sensor.length * cos(radians(rotation))
            end_y = start_y + sensor.length * sin(radians(rotation))

            line = ShapeUtils.get_line(start_x, start_y, end_x, end_y, batch=batch)

            car.metadata["sensors"][str(sensor.angle_offset)] = line

        # print(f"Value of sensors is {[sensor.value for sensor in car.wall_sensors]}")
