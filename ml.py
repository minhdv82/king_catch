from abc import ABC, abstractmethod

import torch
from torch import nn
from torch.utils.data import DataLoader


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
        super().__init__(*args, **kwargs)
    
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




