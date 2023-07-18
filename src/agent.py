from abc import ABC, abstractmethod

from .configs import Agent_Type, AI_DEPTH
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
        return LOSS
    moves_us, moves_them = gen_moves(game_state.blocks, game_state.king_us_pos), gen_moves(game_state.blocks, game_state.king_them_pos)
    if len(moves_us) == 0:
        return LOSS
    if len(moves_them) == 0:
        return WIN
    return len(moves_us) - len(moves_them)


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
        self._thinking = False

    @property
    def is_thinking(self):
        return self._thinking

    def make_move(self, game_state: Game_State, side_to_move: int) -> Move:
        if self._thinking:
            return None
        # return self._random_search(game_state, side_to_move)
        self._thinking = True
        move = self._alpha_beta_search(game_state, side_to_move)
        self._thinking = False
        return move
    
    def _random_search(self, game_state: Game_State, side_to_move: int) -> Move:
        moves = gen_moves(game_state.blocks, game_state.king_us_pos)
        if moves is not None:
            return Move(side_to_move, Position(moves[0].row, moves[0].col))
        return None
    
    def _alpha_beta_search(self, game_state: Game_State, side_to_move: int):
        def _alpha_beta(game_state: Game_State, depth: int, lo: int, hi: int, lohi: int):
            if game_state.king_them_pos == game_state.king_us_pos:
                return (LOSS * lohi, [])
            if depth == 0:
                return (lohi * eval_state(game_state), [])
            moves = gen_moves(game_state.blocks, game_state.king_us_pos)
            if len(moves) == 0:
                return (LOSS * lohi, [])
            
            if lohi > 0:
                opt_val, opt_seq = LOSS, None
                for move in moves:
                    do_move(game_state, move)
                    val, seq = _alpha_beta(game_state, depth - 1, lo, hi, -lohi)
                    undo_move(game_state)
                    if val >= opt_val:
                        seq.append(move)
                        opt_val = val
                        opt_seq = seq
                    lo = max(lo, opt_val)
                    if lo >= hi:
                        return (opt_val, opt_seq)
                return (opt_val, opt_seq)
            else:
                opt_val, opt_seq = WIN, None
                for move in moves:
                    do_move(game_state, move)
                    val, seq = _alpha_beta(game_state, depth - 1, lo, hi, -lohi)
                    undo_move(game_state)
                    if val <= opt_val:
                        seq.append(move)
                        opt_val = val
                        opt_seq = seq
                    hi = min(hi, opt_val)
                    if lo >= hi:
                        return (opt_val, opt_seq)
                return (opt_val, opt_seq)

        def _minimax(depth, game_state: Game_State, lo, hi):
            opt_val = eval_state(game_state)
            if depth == 0 or opt_val == LOSS or opt_val == WIN:
                return (opt_val, [])
            moves = gen_moves(game_state.blocks, game_state.king_us_pos)
            opt_val, opt_move = WIN, []
            for move in moves:
                do_move(game_state, move)
                res, seq = _minimax(depth - 1, game_state, lo, hi)
                undo_move(game_state)
                if res <= LOSS:
                    seq.append(move)
                    return (WIN, seq)
                if res <= opt_val:
                    seq.append(move)
                    opt_val = res
                    opt_move = seq
            return (-opt_val, opt_move)
        
        # if game_state.king_them_pos is None:
        #     opt_val, opt_move = LOSS, None
        #     last_pos = game_state.traces[-1]
        #     king_thems = gen_moves(game_state.blocks, last_pos)
        #     for king_them_pos in king_thems:
        #         game_state.king_them_pos = king_them_pos
        #         val, move = _minimax(depth=AI_DEPTH, game_state=game_state, lo=LOSS, hi=WIN)
        #         game_state.king_them_pos = None
        #         if val > opt_val:
        #             opt_val, opt_move = val, move
        # else:
        #     opt_val, opt_move = _minimax(depth=AI_DEPTH, game_state=game_state, lo=LOSS, hi=WIN)
        opt_val, opt_move = _alpha_beta(game_state, AI_DEPTH, LOSS, WIN, 1)
        if opt_move:
            opt_move = opt_move[::-1]
            move = Position(opt_move[0].row, opt_move[0].col)
        else:
            move = gen_moves(game_state.blocks, game_state.king_us_pos)[0]
            move = Position(move.row, move.col)
        if opt_val == WIN:
            print('win')
            l = min(8, len(opt_move))
            print(opt_move[:l])
        elif opt_val == LOSS:
            print('lose')
            l = min(8, len(opt_move))
            print(opt_move[:l])

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
