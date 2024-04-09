from pyglet.graphics import Batch
from pyglet import shapes
import webcolors


class Shaper:
    point_size = 5

    @classmethod
    def get_point(cls, x: int, y: int, color: str, batch: Batch):
        return shapes.Circle(
            x=x,
            y=y,
            radius=cls.point_size,
            color=webcolors.name_to_rgb(color),
            batch=batch,
        )
