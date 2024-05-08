from math import inf
import numpy as np
from entities.rectangle import Rectangle


class Geometry:
    @classmethod
    def translate_point(cls, point, vector):
        return point + vector

    @classmethod
    def rotate_point(cls, point, angle, origin=np.array([0, 0])):
        rad = np.deg2rad(angle)
        rotation_matrix = np.array(
            [[np.cos(rad), -np.sin(rad)], [np.sin(rad), np.cos(rad)]]
        )
        translated_point = point - origin
        rotated_point = rotation_matrix @ translated_point
        return rotated_point + origin

    @classmethod
    def scale_point(cls, point, scale_factor, origin=np.array([0, 0])):
        return origin + scale_factor * (point - origin)

    @staticmethod
    def normalize_vector(vec: np.ndarray) -> np.ndarray:
        return vec / np.linalg.norm(vec)

    @classmethod
    def get_rotated_rectangle(cls, origin, width, height, angle) -> Rectangle:
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

    @staticmethod
    def project_polygon(axis, polygon):
        projected = [np.dot(vertex, axis) for vertex in polygon]
        return min(projected), max(projected)

    @classmethod
    def are_colliding(
        cls, rect1: Rectangle, rect2: Rectangle
    ) -> tuple[bool, np.ndarray, float]:
        edges = []
        normal = np.array([0.0, 0.0])
        depth = inf
        for rect in (rect1, rect2):
            points = rect.points
            for i in range(len(points)):
                edge_vec = points[i] - points[i - 1]
                axis = np.array([-edge_vec[1], edge_vec[0]])
                axis = cls.normalize_vector(axis)
                edges.append(axis)

        # For each axis (normal to the edges), project and check for overlap
        for axis in edges:
            p1_min, p1_max = Geometry.project_polygon(axis, rect1.points)
            p2_min, p2_max = Geometry.project_polygon(axis, rect2.points)

            if p1_max < p2_min or p2_max < p1_min:
                return False, normal, depth

            axis_depth = min(p2_max - p1_min, p1_max - p2_min)
            if axis_depth < depth:
                normal = axis
                depth = axis_depth

        # Fix normal direction to be from rect2 to rect1
        direction = rect2.center - rect1.center
        if np.dot(direction, normal) < 0:
            normal = -normal
        return True, normal, depth  # All projections overlap, rectangles collide

    @staticmethod
    def get_distance(p1: np.ndarray, p2: np.ndarray) -> float:
        return float(np.linalg.norm(p2 - p1))
