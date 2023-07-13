from abc import ABC, abstractmethod

from .configs import AI, HUMAN
from .base import *


class Agent(ABC):
    def __init__(self) -> None:
        self.type = None
    
    @abstractmethod
    def make_move(self, board: Board, side_to_move: int) -> Move:
        raise NotImplementedError


class AI(Agent):
    def __init__(self) -> None:
        super().__init__()
        self.type = AI
    def make_move(self, board: Board, side_to_move: int) -> Move:
        import random
        while True:
            row, col = random.randint(0, NUM_ROWS), random.randint(0, NUM_COLS)
            move = Move(side=side_to_move, pos=Position(row, col))
            if board.check_move(move).value != Move_Type.INVALID:
                return move


class Human(Agent):
    def __init__(self) -> None:
        super().__init__()
        self.type = HUMAN

    def make_move(self, board: Board, side_to_move: int) -> Move:
        while True:
            board.draw()
            s = input('Please make a move: ')
            s = s.split()
            row, col = int(s[0]), int(s[1])
            move = Move(side=side_to_move, pos=Position(row, col))
            if board.check_move(move).value != Move_Type.INVALID:
                return move
