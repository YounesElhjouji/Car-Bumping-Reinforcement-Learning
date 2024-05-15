from collections import deque
import random
import numpy as np
from random import choice, randint

import torch

from entities.action import Action, State
from pytorch.model import QNetModel, QNetTrainer

MEMORY_SIZE = 100_000
BATCH_SIZE = 1000
LR = 0.001
GAMMA = 0.9


class Agent:
    def __init__(self) -> None:
        self.n_games = 0
        self.memory = deque(maxlen=MEMORY_SIZE)
        self.model = QNetModel(14, 256, 128, 9)
        self.trainer = QNetTrainer(self.model, lr=LR, gamma=GAMMA)

    def get_action(self, state: State) -> Action:
        epsilon = 2  # 80 - self.n_games
        if randint(0, 200) < epsilon:
            action = choice(list(Action))
            # print(f"Random action: {action}")
        else:
            state_tensor = torch.tensor(state.to_list(), dtype=torch.float)
            action_tensor = self.model(state_tensor)
            action_index = torch.argmax(action_tensor).item()
            action = Action(action_index + 1)
            # print(f"AI action: {action}")
        return action

    def train_step(
        self, state0: State, state1: State, action: Action, reward: float, done: bool
    ):
        state_old = np.array(state0.to_list())
        action_arr = np.array(action.to_list())
        state_new = np.array(state1.to_list())
        self.trainer.train_step(
            state=state_old,
            action=action_arr,
            reward=reward,
            next_state=state_new,
            done=done,
        )
        self.memory.append((state_old, state_new, action, reward, done))

    def train_batch(self):
        self.n_games += 1
        if len(self.memory) > BATCH_SIZE:
            sample = random.sample(self.memory, BATCH_SIZE)
        else:
            sample = self.memory

            states_old, states_new, actions, rewards, dones = zip(*sample)
            self.trainer.train_step(
                state=states_old,
                action=actions,
                next_state=states_new,
                reward=rewards,
                done=dones,
            )
