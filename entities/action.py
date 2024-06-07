from dataclasses import dataclass
from enum import Enum, auto


class Action(Enum):
    NONE = auto()
    FORWARD = auto()
    BACKWARD = auto()
    LEFT = auto()
    RIGHT = auto()
    FORWARD_LEFT = auto()
    FORWARD_RIGHT = auto()
    BACKWARD_LEFT = auto()
    BACKWARD_RIGHT = auto()

    def to_list(self):
        """Convert an Action enum value to a one-hot list."""
        idx = self.value - 1  # Adjust index since `auto()` starts from 1
        lst = [0] * len(Action)
        lst[idx] = 1
        return lst

    @staticmethod
    def from_list(lst):
        """Convert a one-hot list back to an Action enum value."""
        assert (
            lst.count(1) == 1 and lst.count(0) == len(Action) - 1
        ), "List must be one-hot encoded"
        index = lst.index(1) + 1  # Convert 0-based index to 1-based
        return Action(index)


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
    action = Action.FORWARD
    action_list = action.to_list()
    restored_action = Action.from_list(action_list)
    print(f"Action: {action}, List: {action_list}, Restored Action: {restored_action}")

    state = State(
        x=1.0, y=2.0, speed=-0.5, direction=-1.0, wall_sensors=[0.1, 0.2, 0.3, 0.4]
    )
    state_list = state.to_list()
    restored_state = State.from_list(state_list)
    print(f"Original State: {state}")
    print(f"List: {state_list}")
    print(f"Restored State: {restored_state}")
