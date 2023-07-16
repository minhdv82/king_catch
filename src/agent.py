from abc import ABC, abstractmethod

from .configs import Agent_Type
from .base import *


def gen_moves(blocks, pos):
    row, col = pos.row, pos.col
    cur_pos = rc_2_pos(row, col)
    res = []
    for r in [-1, 0, 1]:
        for c in [-1, 0, 1]:
            if -1 < row + r < NUM_ROWS and -1 < col + c < NUM_COLS:
                pos = rc_2_pos(row + r, col + c)
                if pos == cur_pos:
                    continue
                if blocks[pos] != Block_State.UNFOG:
                    res.append(Position(row + r, col + c))
    return res


class Agent(ABC):
    def __init__(self) -> None:
        self.type = None
    
    @abstractmethod
    def make_move(self, game_state: Game_State) -> Move:
        raise NotImplementedError


class AI(Agent):
    def __init__(self) -> None:
        super().__init__()
        self.type = Agent_Type.AI
    def make_move(self, game_state: Game_State, side_to_move: int) -> Move:
        return self._random_search(game_state, side_to_move)
    
    def _random_search(self, game_state: Game_State, side_to_move: int) -> Move:
        moves = gen_moves(game_state.blocks, game_state.king_us_pos)
        if moves is not None:
            return Move(side_to_move, Position(moves[0].row, moves[0].col))
        return None
    
    def _alpha_beta(self, game_state: Game_State, side_to_move: int) -> Move:
        pass


class Human(Agent):
    def __init__(self, interface='gui') -> None:
        super().__init__()
        self.type = Agent_Type.HUMAN
        self.interface = interface

    def make_move(self, game_state: Game_State) -> Move:
        if self.interface == 'gui':
            return None
        while True:
            s = input('Please make a move: ')
            s = s.split()
            row, col = int(s[0]), int(s[1])
            move = Move(side=side_to_move, pos=Position(row, col))
            return move
