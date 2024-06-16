from dataclasses import dataclass


@dataclass
class State:
    x: float
    y: float
    speed: float
    direction: float
    dx: float
    dy: float
    vx: float
    vy: float  # can be 1.0 or -1.0
    wall_sensors: list[float]

    def to_list(self):
        """Convert a State instance into a list including position, velocity, and wall sensors."""
        return [self.x, self.y, self.speed, self.direction, self.dx, self.dy, self.vx, self.vy] + self.wall_sensors

    @staticmethod
    def from_list(lst):
        """Convert a list back into a State instance."""
        x = lst[0]
        y = lst[1]
        speed = lst[2]
        direction = lst[3]
        dx = lst[4]
        dy = lst[5]
        vx = lst[6]
        vy = lst[7]
        wall_sensors = lst[8:]
        return State(x, y, speed, direction, dx, dy, vx, vy, wall_sensors)


if __name__ == "__main__":
    state = State(
        x=1.0, y=2.0, speed=-0.5, direction=-1.0, dx=1.0, dy=2.0, vx=-0.5, vy=-1.0, wall_sensors=[0.1, 0.2, 0.3, 0.4]
    )
    state_list = state.to_list()
    restored_state = State.from_list(state_list)
    print(f"Original State: {state}")
    print(f"List: {state_list}")
    print(f"Restored State: {restored_state}")
