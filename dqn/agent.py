from collections import deque
import random
import numpy as np
from random import choice, randint

import torch

from entities.action import OneHotAction
from entities.state import State
from dqn.model import QNetModel, QNetTrainer

MEMORY_SIZE = 10000
BATCH_SIZE = 1000
LR = 0.01
GAMMA = 0.95


class QNetAgent:
    def __init__(self, arch: list[int]) -> None:
        self.n_games = 0
        self.model = QNetModel(arch)
        self.target_model = QNetModel(arch)
        self.memory = deque(maxlen=MEMORY_SIZE)
        self.trainer = QNetTrainer(self.model, self.target_model, lr=LR, gamma=GAMMA)

    def get_action(self, state: State) -> OneHotAction:
        epsilon = max(5, 80 - self.n_games)
        if randint(0, 200) < epsilon:
            action = choice(list(OneHotAction))
            # print(f"Random action: {action}")
        else:
            state_tensor = torch.tensor(state.to_list(), dtype=torch.float)
            action_tensor = self.model(state_tensor)
            action_index = torch.argmax(action_tensor).item()
            action = OneHotAction(action_index + 1)
            # print(f"AI action: {action}")
        return action

    def train_step(
        self,
        state0: State,
        state1: State,
        action: OneHotAction,
        reward: float,
        done: bool,
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
        self.memory.append((state_old, state_new, action_arr, reward, done))

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

    def update_target_network(self):
        self.target_model.load_state_dict(
            self.model.state_dict()
        )  # Update target network
