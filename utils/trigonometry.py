import numpy as np
from entities.rectangle import Rectangle


class TrigUtils:
    @classmethod
    def translate_point(cls, point, vector):
        """
        Translates a point by a given vector.

        :param point: np.array, the point to translate, format: [x, y]
        :param vector: np.array, the translation vector, format: [dx, dy]
        :return: np.array, the translated point
        """
        return point + vector

    @classmethod
    def rotate_point(cls, point, angle, origin=np.array([0, 0])):
        """
        Rotates a point around a given origin by an angle in degrees.

        :param point: np.array, the point to rotate, format: [x, y]
        :param angle: float, rotation angle in degrees
        :param origin: np.array, the point around which to rotate, format: [x, y]
        :return: np.array, the rotated point
        """
        rad = np.deg2rad(angle)
        rotation_matrix = np.array(
            [[np.cos(rad), -np.sin(rad)], [np.sin(rad), np.cos(rad)]]
        )
        translated_point = point - origin
        rotated_point = rotation_matrix @ translated_point
        return rotated_point + origin

    @classmethod
    def scale_point(cls, point, scale_factor, origin=np.array([0, 0])):
        """
        Scales a point relative to a given origin.

        :param point: np.array, the point to scale, format: [x, y]
        :param scale_factor: float or np.array, the scale factor
        :param origin: np.array, the point relative to which to scale, format: [x, y]
        :return: np.array, the scaled point
        """
        return origin + scale_factor * (point - origin)

    @classmethod
    def get_rotated_rectangle(cls, origin, width, height, angle) -> Rectangle:
        """
        Computes the corners of a rotated rectangle.

        :param origin: np.array, the origin point (first corner), format: [x, y]
        :param width: float, the width of the rectangle
        :param height: float, the height of the rectangle
        :param angle: float, rotation angle in degrees
        :return: list of np.array, list of corners of the rectangle
        """
        corners = [
            origin,
            cls.translate_point(origin, np.array([width, 0])),
            cls.translate_point(origin, np.array([width, height])),
            cls.translate_point(origin, np.array([0, height])),
        ]
        corners = [cls.rotate_point(corner, angle, origin) for corner in corners]
        rect = Rectangle(
            bot_left=origin,
            bot_right=corners[1],
            top_right=corners[2],
            top_left=corners[3],
        )
        return rect
