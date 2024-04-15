from pyglet.graphics import Batch
from pyglet.resource import Loader
from pyglet.sprite import Sprite


class PygletUtils:
    @staticmethod
    def create_car_sprite(width: int, batch: Batch) -> Sprite:
        my_image = Loader(path="resources").image(name="car1.png")
        car_sprite: Sprite = Sprite(img=my_image, batch=batch)
        car_sprite.scale = width / car_sprite.width
        car_sprite.image.anchor_x = car_sprite.width // 2
        car_sprite.image.anchor_y = car_sprite.height // 2
        return car_sprite

    @staticmethod
    def create_fire_sprite(car_height: int, batch: Batch) -> Sprite:
        my_image = Loader(path="resources").image(name="fire.png")
        fire_sprite = Sprite(my_image, batch=batch)
        fire_sprite.anchor_x = fire_sprite.width
        fire_sprite.anchor_y = fire_sprite.height / 2
        fire_sprite.scale = 0.8 * car_height / fire_sprite.height
        return fire_sprite
