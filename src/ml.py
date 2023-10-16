from abc import ABC, abstractmethod

import torch
from torch import nn
from torch.utils.data import DataLoader
from base import Move

from sim import *
from agent import Agent

class Data(ABC, DataLoader):
    def __init__(self, *args, **kwargs):
        super().__init__()
    
    @abstractmethod
    def fetch_batch(self):
        raise NotImplementedError("Please implement the method")
    
    def __getitem__(self, idx):
        pass

    def __len__(self):
        pass


class CausalModel(nn.Module):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(args, kwargs)
    
    def from_pretrained(self):
        pass

    def forward(self, x):
        pass


class Trainer():
    def __init__(self, model, data_loader) -> None:
        self._model = model
        self._data_loader = data_loader
        
    def train(self):
        pass


class RLAgent(Agent):
    def __init__(self, sim, lr=0.01, gamma=0.9, epsilon=0.9, epsilon_min=0.15, epsilon_decay=0.95) -> None:
        super().__init__()
        self.sim = sim
        self.lr = lr
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_dcay = epsilon_decay

    def get_move(self) -> Move:
        return super().get_move()

    def learn(self):
        pass

    def act(self):
        pass
