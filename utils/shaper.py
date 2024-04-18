from pyglet.graphics import Batch
import numpy as np
from math import sin, cos, radians
from pyglet import shapes
import webcolors

from car import Car
from entities.body import Body
from utils.trigonometry import TrigUtils


class ShapeUtils:
    point_size = 3

    @classmethod
    def get_point(cls, x: int, y: int, color: str, batch: Batch):
        return shapes.Circle(
            x=x,
            y=y,
            radius=cls.point_size,
            color=webcolors.name_to_rgb(color),
            batch=batch,
        )

    @classmethod
    def draw_debug_visuals(cls, car: Car, batch: Batch):
        px, py = car.body.position
        x, y = cls.get_center(car.body)
        center = cls.get_point(x=x, y=y, color="green", batch=batch)
        pos = ShapeUtils.get_point(x=px, y=py, color="red", batch=batch)
        body = car.body
        rect = TrigUtils.get_rotated_rectangle(
            origin=body.position,
            width=body.width,
            height=body.height,
            angle=body.rotation,
        )
        # car.debug_visuals.update(
        #     {
        #         "pos": pos,
        #         "center": center,
        #         "points": [
        #             cls.get_point(x=p[0], y=p[1], color="orange", batch=batch)
        #             for p in rect.points
        #         ],
        #     }
        # )

    @staticmethod
    def get_portion(body: Body, is_x: bool):
        width = body.width
        height = body.height
        angle = radians(body.rotation)
        if is_x:
            return width * cos(angle) - height * sin(angle)
        else:
            return width * sin(angle) + height * cos(angle)

    @classmethod
    def get_center(cls, body: Body):
        return np.array(
            [
                body.position[0] + 0.5 * cls.get_portion(body, is_x=True),
                body.position[1] + 0.5 * cls.get_portion(body, is_x=False),
            ]
        )
