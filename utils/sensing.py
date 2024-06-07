import numpy as np
from pyglet.graphics import Batch

from car import Car
from entities.car_collection import CarCollection
from entities.rectangle import Rectangle
from entities.sensor import Sensor
from entities.world import World
from utils.shaper import ShapeUtils
from utils.geometry import Geometry


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

        for sensor in car.wall_sensors:
            value = 1.0  # distance to closest wall [0.0, 1.0]
            for rect in cls.get_wall_rectangles():
                intersection = cls.line_rectangle_collision(sensor, rect)
                if intersection is None:
                    continue
                distance = Geometry.get_distance(car.body.car_rect.center, intersection)
                value = min(value, distance / sensor.length)
                point = ShapeUtils.get_point(
                    intersection[0], intersection[1], color="purple", batch=batch
                )
                car.metadata["wall_sensor_detections"].append(point)
            sensor.value = 1.0 - value

    @classmethod
    def sense_cars(cls, car: Car, car_collection: CarCollection, batch: Batch):
        car.metadata["car_sensor_detections"] = []
        car.metadata["bumper_sensor_detections"] = []
        for other_car in [c for c in car_collection.cars if c.id_ != car.id_]:
            rect = other_car.body.car_rect
            if (
                Geometry.get_distance(car.body.position, other_car.body.position)
                > Sensor.length
            ):
                continue
            for idx, sensor in enumerate(car.car_sensors):
                intersection = cls.line_rectangle_collision(sensor, rect)
                if intersection is None:
                    continue

                is_bumper = cls.sense_bumper(
                    car=car,
                    other=other_car,
                    sensor_idx=idx,
                    car_intersection=intersection,
                    batch=batch,
                )
                if not is_bumper:
                    point = ShapeUtils.get_point(
                        intersection[0], intersection[1], color="purple", batch=batch
                    )
                    car.metadata["car_sensor_detections"].append(point)

    @classmethod
    def sense_bumper(
        cls,
        car: Car,
        other: Car,
        sensor_idx: int,
        car_intersection: np.ndarray,
        batch: Batch,
    ):
        bumper_rect = other.body.bumper_rect
        sensor = car.bumper_sensors[sensor_idx]
        bumper_intersection = cls.line_rectangle_collision(sensor, bumper_rect)

        # helper function returns if bumper is sensed without car obstruction
        def is_bumper_visible():
            car_distance = np.linalg.norm(sensor.position - car_intersection)
            bumper_distance = np.linalg.norm(sensor.position - bumper_intersection)
            return abs(bumper_distance - car_distance) < 2

        if bumper_intersection is not None and is_bumper_visible():
            point = ShapeUtils.get_point(
                bumper_intersection[0], bumper_intersection[1], color="red", batch=batch
            )
            car.metadata["bumper_sensor_detections"].append(point)
            return True
        return False

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
