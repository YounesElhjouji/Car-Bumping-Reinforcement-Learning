from pyglet.graphics import Batch
import numpy as np
from math import sin, cos, radians
from pyglet import shapes
import webcolors

from car import Car
from entities.body import Body
from entities.rectangle import Rectangle
from utils.geometry import Geometry


class ShapeUtils:
    point_size = 3

    @classmethod
    def get_point(cls, x: int, y: int, color: str, batch: Batch):
        return shapes.Circle(
            x=x,
            y=y,
            radius=cls.point_size,
            color=cls.to_rgba(color),
            batch=batch,
        )

    @staticmethod
    def to_rgba(color: str) -> tuple[int, ...]:
        rgb = webcolors.name_to_rgb(color)
        return rgb + (128,)

    @classmethod
    def get_rectangle(cls, rect: Rectangle, color: str, batch: Batch):
        return shapes.Polygon(
            *[p.tolist() for p in rect.points],
            color=cls.to_rgba(color),
            batch=batch,
        )

    @classmethod
    def draw_debug_visuals(cls, car: Car, batch: Batch):
        px, py = car.body.position
        x, y = cls.get_center(car.body)
        center = cls.get_point(x=x, y=y, color="green", batch=batch)
        pos = cls.get_point(x=px, y=py, color="red", batch=batch)
        body = car.body
        rect = Geometry.get_rotated_rectangle(
            origin=body.position,
            width=body.width,
            height=body.height,
            angle=body.rotation,
        )
        bumper = cls.get_rectangle(rect=car.body.bumper_rect, color="blue", batch=batch)
        car.debug_visuals.update(
            {
                # "pos": pos,
                # "center": center,
                # "points": [
                #     cls.get_point(x=p[0], y=p[1], color="orange", batch=batch)
                #     for p in rect.points
                # ],
                "bumper": bumper
            }
        )

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

    @classmethod
    def get_line(cls, x1: int, y1: int, x2: int, y2: int, batch: Batch, width: int = 1):
        return shapes.Line(
            x=x1,
            y=y1,
            x2=x2,
            y2=y2,
            width=width,
            color=cls.to_rgba("grey"),
            batch=batch,
        )
