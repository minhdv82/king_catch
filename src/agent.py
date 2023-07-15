from abc import ABC, abstractmethod

from .configs import Agent_Type
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
        self.type = Agent_Type.AI
    def make_move(self, board: Board, side_to_move: int) -> Move:
        moves = board.get_moves(side_to_move)
        if moves is not None:
            return Move(side_to_move, Position(moves[0].row, moves[0].col))
        return None
class Human(Agent):
    def __init__(self, interface='gui') -> None:
        super().__init__()
        self.type = Agent_Type.HUMAN
        self.interface = interface

    def make_move(self, board: Board, side_to_move: int) -> Move:
        if self.interface == 'gui':
            return None
        while True:
            s = input('Please make a move: ')
            s = s.split()
            row, col = int(s[0]), int(s[1])
            move = Move(side=side_to_move, pos=Position(row, col))
            if board.check_move(move) != Move_Type.INVALID:
                return move
