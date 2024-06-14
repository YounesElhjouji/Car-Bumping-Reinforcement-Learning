import os
from dotenv import load_dotenv

load_dotenv()


def get_world_size() -> tuple[int, ...]:
    window_size = tuple(map(int, os.getenv("WINDOW_SIZE", "100,100").split(",")))
    return window_size


if __name__ == "__main__":
    print(get_world_size())
