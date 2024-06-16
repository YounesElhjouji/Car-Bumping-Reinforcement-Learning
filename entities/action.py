from dataclasses import dataclass
from enum import Enum, auto


class OneHotAction(Enum):
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
        lst = [0] * len(OneHotAction)
        lst[idx] = 1
        return lst

    @staticmethod
    def from_list(lst):
        """Convert a one-hot list back to an Action enum value."""
        assert (
            lst.count(1) == 1 and lst.count(0) == len(OneHotAction) - 1
        ), "List must be one-hot encoded"
        index = lst.index(1) + 1  # Convert 0-based index to 1-based
        return OneHotAction(index)


@dataclass
class MultiAction:
    forward: bool
    backward: bool
    left: bool
    right: bool
    turbo: bool

    def to_list(self):
        return [self.forward, self.backward, self.left, self.right, self.turbo]

    @classmethod
    def from_list(cls, lst: list):
        return cls(
            forward=lst[0],
            backward=lst[1],
            left=lst[2],
            right=lst[3],
            turbo=lst[4],
        )


if __name__ == "__main__":
    action = OneHotAction.FORWARD
    action_list = action.to_list()
    restored_action = OneHotAction.from_list(action_list)
    print(f"Action: {action}, List: {action_list}, Restored Action: {restored_action}")

    action = MultiAction(
        forward=True, backward=False, left=False, right=True, turbo=False
    )
    action_list = action.to_list()
    restored_action = MultiAction.from_list(action_list)
    print(f"Action: {action}, List: {action_list}, Restored Action: {restored_action}")
