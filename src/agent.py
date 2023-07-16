from abc import ABC, abstractmethod

from .configs import Agent_Type
from .base import *


LOSS, WIN = -1000_000, 1000_000


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


def do_move(game_state: Game_State, move: Move):
    us_pos, them_pos = game_state.king_us_pos, game_state.king_them_pos
    game_state.traces.append(Position(us_pos.row, us_pos.col))
    game_state.blocks[rc_2_pos(us_pos.row, us_pos.col)] = Block_State.UNFOG
    us_pos.row, us_pos.col = them_pos.row, them_pos.col
    them_pos.row, them_pos.col = move.row, move.col


def undo_move(game_state: Game_State):
    us_pos, them_pos = game_state.king_us_pos, game_state.king_them_pos
    them_pos.row, them_pos.col = us_pos.row, us_pos.col
    us_pos.row, us_pos.col = game_state.traces[-1].row, game_state.traces[-1].col
    game_state.blocks[rc_2_pos(them_pos.row, them_pos.col)] = Block_State.FOG
    game_state.traces.pop()


def eval_state(game_state: Game_State) -> int:
    if game_state.king_us_pos == game_state.king_them_pos:
        print('clash')
        return LOSS
    moves = gen_moves(game_state.blocks, game_state.king_us_pos)
    if len(moves) == 0:
        return LOSS
    return len(moves)


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
        # return self._random_search(game_state, side_to_move)
        return self._alpha_beta_search(game_state, side_to_move)
    
    def _random_search(self, game_state: Game_State, side_to_move: int) -> Move:
        moves = gen_moves(game_state.blocks, game_state.king_us_pos)
        if moves is not None:
            return Move(side_to_move, Position(moves[0].row, moves[0].col))
        return None
    
    def _alpha_beta_search(self, game_state: Game_State, side_to_move: int):
        def _minimax(depth, game_state, lo, hi):
            if depth == 0:
                return (eval_state(game_state), None)
            moves = gen_moves(game_state.blocks, game_state.king_us_pos)
            if len(moves) == 0:
                return (LOSS, None)
            opt_val, opt_move = WIN, None
            for move in moves:
                do_move(game_state, move)
                res, _ = _minimax(depth - 1, game_state, lo, hi)
                undo_move(game_state)
                if res <= LOSS:
                    return (WIN, move)
                if res < opt_val:
                    opt_val = res
                    opt_move = move
            return (-opt_val, opt_move)
            
        opt_val, opt_move = _minimax(depth=6, game_state=game_state, lo=LOSS, hi=WIN)
        if opt_move is not None:
            move = Position(opt_move.row, opt_move.col)
        else:
            move = gen_moves(game_state.blocks, game_state.king_us_pos)
            move = Position(move.row, move.col)

        return Move(side_to_move, move)


class Human(Agent):
    def __init__(self, interface='gui') -> None:
        super().__init__()
        self.type = Agent_Type.HUMAN
        self.interface = interface

    def make_move(self, game_state: Game_State, side_to_move: int) -> Move:
        if self.interface == 'gui':
            return None
        while True:
            s = input('Please make a move: ')
            s = s.split()
            row, col = int(s[0]), int(s[1])
            move = Move(side=side_to_move, pos=Position(row, col))
            return move
