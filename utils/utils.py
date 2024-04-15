import os
from dotenv import load_dotenv

load_dotenv()


def get_window_size() -> tuple[int, ...]:
    window_size = tuple(map(int, os.getenv("WINDOW_SIZE").split(",")))
    return window_size


if __name__ == "__main__":
    print(get_window_size())
