import numpy as np
from pyglet.graphics import Batch

from car import Car
from entities.rectangle import Rectangle
from entities.sensor import Sensor
from entities.world import World
from utils.shaper import ShapeUtils


class SensingUtils:
    @staticmethod
    def get_wall_rectangles():
        walls = []
        screen_width, screen_height = World.size
        wall_thickness = 100

        # Left wall
        walls.append(
            Rectangle(
                top_left=np.array([-wall_thickness, screen_height + wall_thickness]),
                bot_left=np.array([-wall_thickness, -wall_thickness]),
                bot_right=np.array([0, -wall_thickness]),
                top_right=np.array([0, screen_height + wall_thickness]),
            )
        )

        # Right wall
        walls.append(
            Rectangle(
                top_left=np.array([screen_width, screen_height + wall_thickness]),
                bot_left=np.array([screen_width, -wall_thickness]),
                bot_right=np.array([screen_width + wall_thickness, -wall_thickness]),
                top_right=np.array(
                    [screen_width + wall_thickness, screen_height + wall_thickness]
                ),
            )
        )

        # Top wall
        walls.append(
            Rectangle(
                top_left=np.array([-wall_thickness, screen_height + wall_thickness]),
                bot_left=np.array([-wall_thickness, screen_height]),
                bot_right=np.array([screen_width + wall_thickness, screen_height]),
                top_right=np.array(
                    [screen_width + wall_thickness, screen_height + wall_thickness]
                ),
            )
        )

        # Bottom wall
        walls.append(
            Rectangle(
                top_left=np.array([-wall_thickness, -wall_thickness]),
                bot_left=np.array([-wall_thickness, -wall_thickness - wall_thickness]),
                bot_right=np.array(
                    [screen_width + wall_thickness, -wall_thickness - wall_thickness]
                ),
                top_right=np.array([screen_width + wall_thickness, -wall_thickness]),
            )
        )

        return walls

    @classmethod
    def sense_walls(cls, car: Car, batch: Batch):
        car.metadata["sensor_detections"] = []
        for rect in cls.get_wall_rectangles():
            for sensor in car.sensors:
                intersection = cls.line_rectangle_collision(sensor, rect)
                if intersection is None:
                    continue

                point = ShapeUtils.get_point(
                    intersection[0], intersection[1], color="purple", batch=batch
                )
                car.metadata["sensor_detections"].append(point)

    @staticmethod
    def line_rectangle_collision(
        sensor: Sensor, rectangle: Rectangle
    ) -> np.ndarray | None:
        # Get the line start and end points
        line_start = sensor.position
        line_end = (
            line_start
            + np.array([np.cos(sensor.rotation), np.sin(sensor.rotation)])
            * sensor.length
        )
        # Get the rectangle corners
        rect_corners = rectangle.points
        # Initialize the closest intersection point
        closest_intersection = None
        closest_distance = np.inf
        # Check for intersection with each rectangle edge
        for i in range(len(rect_corners)):
            p1 = rect_corners[i]
            p2 = rect_corners[(i + 1) % len(rect_corners)]
            # Calculate the line segment vectors
            line_vec = line_end - line_start
            edge_vec = p2 - p1
            # Calculate the perpendicular vector of the line
            perp_vec = np.array([-line_vec[1], line_vec[0]])
            # Calculate the distances from the line to the edge endpoints
            dist1 = np.dot(p1 - line_start, perp_vec)
            dist2 = np.dot(p2 - line_start, perp_vec)
            # Check if the line intersects the edge
            if dist1 * dist2 <= 0:
                # Calculate the intersection point
                intersection = line_start + line_vec * (
                    np.cross(edge_vec, p1 - line_start) / np.cross(edge_vec, line_vec)
                )
                # Check if the intersection point is within the line segment
                t = np.dot(intersection - line_start, line_vec) / np.dot(
                    line_vec, line_vec
                )
                if 0 <= t <= 1:
                    # Calculate the distance from the intersection point to the line origin
                    distance = np.linalg.norm(intersection - line_start)
                    # Update the closest intersection point if necessary
                    if distance < closest_distance:
                        closest_intersection = intersection
                        closest_distance = distance
        return closest_intersection
