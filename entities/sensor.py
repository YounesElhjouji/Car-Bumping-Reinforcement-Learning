from bson import ObjectId

from entities.body import Body


class Sensor:
    length: int = 200

    def __init__(self, body: Body, angle_offset: float, car_id: ObjectId) -> None:
        self.position = body.rectangle.center
        self.angle_offset = angle_offset
        self.rotation = body.rotation + angle_offset
        self.car_id = car_id

    def update_sensor(self, body: Body):
        self.position = body.rectangle.center
        self.rotation = body.rotation + self.angle_offset
