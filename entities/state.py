from dataclasses import dataclass


@dataclass
class State:
    x: float
    y: float
    speed: float
    direction: float  # can be 1.0 or -1.0
    wall_sensors: list[float]

    def to_list(self):
        """Convert a State instance into a list including position, velocity, and wall sensors."""
        return [self.x, self.y, self.speed, self.direction] + self.wall_sensors

    @staticmethod
    def from_list(lst):
        """Convert a list back into a State instance."""
        x = lst[0]
        y = lst[1]
        speed = lst[2]
        direction = lst[3]
        wall_sensors = lst[4:]
        return State(x, y, speed, direction, wall_sensors)


if __name__ == "__main__":
    state = State(
        x=1.0, y=2.0, speed=-0.5, direction=-1.0, wall_sensors=[0.1, 0.2, 0.3, 0.4]
    )
    state_list = state.to_list()
    restored_state = State.from_list(state_list)
    print(f"Original State: {state}")
    print(f"List: {state_list}")
    print(f"Restored State: {restored_state}")
