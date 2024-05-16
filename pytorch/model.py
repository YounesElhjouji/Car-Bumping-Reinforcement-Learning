import torch
import torch.nn as nn
from torch.nn.functional import relu


class QNetModel(nn.Module):
    def __init__(self, arch: list[int]):
        super().__init__()
        self.arch = arch
        self.layers = nn.ModuleList()
        for i in range(len(arch) - 1):
            inp, out = arch[i], arch[i + 1]
            self.layers.append(nn.Linear(inp, out))

    def forward(self, x):
        for layer in self.layers[:-1]:
            x = layer(x)
            x = relu(x)
        x = self.layers[-1](x)  # output layer
        return x

    def save(self, file_path: str = "../resources/model.pth"):
        torch.save(self.state_dict(), file_path)


class QNetTrainer:
    def __init__(self, model, lr, gamma):
        self.lr = lr
        self.gamma = gamma
        self.model = model
        self.optimizer = torch.optim.Adam(model.parameters(), lr=self.lr)
        self.criterion = nn.MSELoss()

    def train_step(self, state, action, reward, next_state, done):
        state = torch.tensor(state, dtype=torch.float)
        next_state = torch.tensor(next_state, dtype=torch.float)
        action = torch.tensor(action, dtype=torch.long)
        reward = torch.tensor(reward, dtype=torch.float)
        # (n, x)

        if len(state.shape) == 1:
            # (1, x)
            state = torch.unsqueeze(state, 0)
            next_state = torch.unsqueeze(next_state, 0)
            action = torch.unsqueeze(action, 0)
            reward = torch.unsqueeze(reward, 0)
            done = (done,)

        # 1: predicted Q values with current state
        pred = self.model(state)

        target = pred.clone()
        for idx in range(len(done)):
            Q_new = reward[idx]
            if not done[idx]:
                Q_new = reward[idx] + self.gamma * torch.max(
                    self.model(next_state[idx])
                )

            target[idx][torch.argmax(action[idx]).item()] = Q_new

        self.optimizer.zero_grad()
        loss = self.criterion(target, pred)
        loss.backward()

        self.optimizer.step()


if __name__ == "__main__":
    model = QNetModel([3, 2])
    input_tensor = torch.tensor([0.5, 1.0, 0.0], dtype=torch.float)
    output_tensor = model(input_tensor)
    print(f"output {output_tensor}")
