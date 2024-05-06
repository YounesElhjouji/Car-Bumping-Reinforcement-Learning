import numpy as np
from pyglet.graphics import Batch

from car import Car
from entities.car_collection import CarCollection
from entities.rectangle import Rectangle
from entities.sensor import Sensor
from entities.world import World
from utils.shaper import ShapeUtils


class SensingUtils:
    lines = []
    intersection = []

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
                top_left=np.array([-wall_thickness, 0]),
                bot_left=np.array([-wall_thickness, -wall_thickness]),
                bot_right=np.array([screen_width + wall_thickness, -wall_thickness]),
                top_right=np.array([screen_width + wall_thickness, 0]),
            )
        )

        return walls

    @classmethod
    def sense_walls(cls, car: Car, batch: Batch):
        car.metadata["wall_sensor_detections"] = []
        for rect in cls.get_wall_rectangles():
            for sensor in car.wall_sensors:
                intersection = cls.line_rectangle_collision(sensor, rect)
                if intersection is None:
                    continue

                point = ShapeUtils.get_point(
                    intersection[0], intersection[1], color="purple", batch=batch
                )
                car.metadata["wall_sensor_detections"].append(point)

    @classmethod
    def sense_cars(cls, car: Car, car_collection: CarCollection, batch: Batch):
        car.metadata["car_sensor_detections"] = []
        for rect in [c.body.rectangle for c in car_collection.cars if c.id_ != car.id_]:
            for sensor in car.car_sensors:
                intersection = cls.line_rectangle_collision(sensor, rect)
                if intersection is None:
                    continue

                point = ShapeUtils.get_point(
                    intersection[0], intersection[1], color="purple", batch=batch
                )
                car.metadata["car_sensor_detections"].append(point)

    @classmethod
    def line_rectangle_collision(
        cls, sensor: Sensor, rectangle: Rectangle
    ) -> np.ndarray | None:
        rect_corners = rectangle.points

        closest_intersection = None
        closest_distance = np.inf

        for i in range(len(rect_corners)):
            p1 = rect_corners[i]
            p2 = rect_corners[(i + 1) % len(rect_corners)]
            intersection = cls.get_segments_intersection(s1=[p1, p2], s2=sensor.points)
            if intersection is not None:
                distance = np.linalg.norm(intersection - sensor.points[0])
                if distance < closest_distance:
                    closest_intersection = intersection
                    closest_distance = distance
        return closest_intersection

    @staticmethod
    def get_segments_intersection(
        s1: list[np.ndarray], s2: list[np.ndarray]
    ) -> np.ndarray | None:
        p1, q1 = s1
        p2, q2 = s2
        r = q1 - p1
        s = q2 - p2
        rxs = r[0] * s[1] - r[1] * s[0]
        if rxs == 0:  # Parallel lines
            return None
        t = (p2[0] - p1[0]) * s[1] - (p2[1] - p1[1]) * s[0]
        u = (p2[0] - p1[0]) * r[1] - (p2[1] - p1[1]) * r[0]
        t /= rxs
        u /= rxs
        if 0 <= t <= 1 and 0 <= u <= 1:
            return p1 + t * r
        return None

    # @classmethod
    # def debug_line_intersection(cls, batch: Batch):
    #     s1 = Sensor(
    #         position=np.array([0, 0]), rotation=45, angle_offset=0, car_id=ObjectId()
    #     )
    #     s2 = Sensor(
    #         position=np.array([100, 0]),
    #         rotation=90 + 45,
    #         angle_offset=0,
    #         car_id=ObjectId(),
    #     )
    #
    #     cls.lines = []
    #     cls.intersection = []
    #
    #     line1 = ShapeUtils.get_line(
    #         s1.points[0][0],
    #         s1.points[0][1],
    #         s1.points[1][0],
    #         s1.points[1][1],
    #         batch=batch,
    #     )
    #     line2 = ShapeUtils.get_line(
    #         s2.points[0][0],
    #         s2.points[0][1],
    #         s2.points[1][0],
    #         s2.points[1][1],
    #         batch=batch,
    #     )
    #
    #     cls.lines = [line1, line2]
    #
    #     intersection = cls.get_segments_intersection(s1.points, s2.points)
    #     if intersection is not None:
    #         print("My debug lines intercept")
    #         point = ShapeUtils.get_point(
    #             intersection[0], intersection[1], color="red", batch=batch
    #         )
    #         cls.intersection.append(point)
