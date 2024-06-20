import torch
import torch.nn as nn
import torch.optim as optim
from torch.distributions import MultivariateNormal
import numpy as np


class PolicyNetwork(nn.Module):
    def __init__(self, input_dim, action_dim, hidden_layers, action_std_init):
        super(PolicyNetwork, self).__init__()
        self.hidden_layers = hidden_layers
        self.layers = nn.ModuleList()
        prev_dim = input_dim
        for hidden_dim in hidden_layers:
            self.layers.append(nn.Linear(prev_dim, hidden_dim))
            self.layers.append(nn.Tanh())
            prev_dim = hidden_dim
        self.layers.append(nn.Linear(prev_dim, action_dim))
        self.layers.append(nn.Tanh())
        self.action_dim = action_dim
        self.log_std = nn.Parameter(torch.ones(action_dim) * action_std_init)

    def forward(self, x):
        for layer in self.layers:
            x = layer(x)
        return x

    def get_dist(self, x):
        mean = self.forward(x)
        std = self.log_std.exp().expand_as(mean)
        cov_matrix = torch.diag_embed(std)
        dist = MultivariateNormal(mean, cov_matrix)
        return dist


class ValueNetwork(nn.Module):
    def __init__(self, input_dim, hidden_layers):
        super(ValueNetwork, self).__init__()
        self.hidden_layers = hidden_layers
        self.layers = nn.ModuleList()
        prev_dim = input_dim
        for hidden_dim in hidden_layers:
            self.layers.append(nn.Linear(prev_dim, hidden_dim))
            self.layers.append(nn.Tanh())
            prev_dim = hidden_dim
        self.layers.append(nn.Linear(prev_dim, 1))

    def forward(self, x):
        for layer in self.layers:
            x = layer(x)
        return x


class PPOAgent:
    def __init__(
        self, input_dim, action_dim, hidden_layers, action_std_init=0.5, lr=3e-4, gamma=0.99, eps_clip=0.2, K_epochs=15
    ):
        self.hidden_layers = hidden_layers
        self.policy = PolicyNetwork(input_dim, action_dim, hidden_layers, action_std_init)
        self.policy_old = PolicyNetwork(input_dim, action_dim, hidden_layers, action_std_init)
        self.policy_old.load_state_dict(self.policy.state_dict())
        self.value_function = ValueNetwork(input_dim, hidden_layers)
        self.optimizer_policy = optim.Adam(self.policy.parameters(), lr=lr)
        self.optimizer_value = optim.Adam(self.value_function.parameters(), lr=lr)
        self.gamma = gamma
        self.eps_clip = eps_clip
        self.K_epochs = K_epochs
        self.mse_loss = nn.MSELoss()

    def select_action(self, state):
        state = torch.FloatTensor(state)
        dist = self.policy_old.get_dist(state)
        action = dist.sample()
        action_logprobs = dist.log_prob(action)
        return action.numpy(), action_logprobs

    def update(self, memory):
        rewards = []
        discounted_reward = 0
        for reward, is_terminal in zip(
            reversed(memory.rewards), reversed(memory.is_terminals)
        ):
            if is_terminal:
                discounted_reward = 0
            discounted_reward = reward + (self.gamma * discounted_reward)
            rewards.insert(0, discounted_reward)

        rewards = torch.tensor(rewards, dtype=torch.float32)
        rewards = (rewards - rewards.mean()) / (rewards.std() + 1e-5)

        old_states = torch.squeeze(torch.stack(memory.states).detach())
        old_actions = torch.squeeze(torch.stack(memory.actions).detach())
        old_logprobs = torch.squeeze(torch.stack(memory.action_probs).detach())

        for _ in range(self.K_epochs):
            logprobs, state_values, dist_entropy = self.evaluate(
                old_states, old_actions
            )

            ratios = torch.exp(logprobs - old_logprobs.detach())
            advantages = rewards - state_values.detach()

            surr1 = ratios * advantages
            surr2 = (
                torch.clamp(ratios, 1 - self.eps_clip, 1 + self.eps_clip) * advantages
            )
            loss = (
                -torch.min(surr1, surr2).mean()
                + 0.8 * self.mse_loss(state_values, rewards)
                - 0.01 * dist_entropy.mean()
            )

            self.optimizer_policy.zero_grad()
            loss.backward()
            self.optimizer_policy.step()

        self.policy_old.load_state_dict(self.policy.state_dict())

    def evaluate(self, state, action):
        dist = self.policy.get_dist(state)
        action_logprobs = dist.log_prob(action)
        dist_entropy = dist.entropy()
        state_values = self.value_function(state)
        return action_logprobs, torch.squeeze(state_values), dist_entropy

    def save_models(self, policy_path, value_path):
        torch.save(self.policy.state_dict(), policy_path)
        torch.save(self.value_function.state_dict(), value_path)
        print(f"Models saved to {policy_path} and {value_path}")

    def load_models(self, policy_path, value_path):
        self.policy.load_state_dict(torch.load(policy_path))
        self.policy_old.load_state_dict(torch.load(policy_path))
        self.value_function.load_state_dict(torch.load(value_path))
        print(f"Models loaded from {policy_path} and {value_path}")


class Memory:
    def __init__(self):
        self.states = []
        self.actions = []
        self.action_probs = []
        self.rewards = []
        self.is_terminals = []

    def clear_memory(self):
        del self.states[:]
        del self.actions[:]
        del self.action_probs[:]
        del self.rewards[:]
        del self.is_terminals[:]
