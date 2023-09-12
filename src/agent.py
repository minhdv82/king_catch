"""
 * Copyright (c) [2023] Minh v. Duong; dvminh82@gmail.com
 *
 * You are free to use, modify, re-distribute this code at your own risk
 */
"""
from abc import ABC, abstractmethod

from .configs import Agent_Type, AI_DEPTH
from .base import *
from .utils import threaded
from .game_model import KingGameModel
from .network import GameClient, GamePacket, MovePacket


LOSS, WIN = -1000_000, 1000_000


def agent_make_move(agent):
    agent.make_move()


class Agent(ABC):
    def __init__(self) -> None:
        self.type = None
    
    @abstractmethod
    def get_move(self) -> Move:
        raise NotImplementedError("Please implement the method!")


class Human(Agent):
    def __init__(self, game_view) -> None:
        super().__init__()
        self.type = Agent_Type.HUMAN
        self._game_view = game_view

    def get_move(self):
        return self._game_view.get_move()


class Bot(Agent):
    def __init__(self, client: GameClient=None) -> None:
        super().__init__()
        self.type = Agent_Type.BOT
        self._client = client
        self._busy = False
        self._data_buffer = []

    @property
    def is_busy(self):
        return self._busy

    def _pop_data(self):
        return self._data_buffer.pop() if self._data_buffer else None

    def get_move(self):
        if self._client is None:
            return None
        return self._client.get_move()

    def get_game(self):
        return self._client.get_game()
        # if self.is_busy:
        #     return None
        # if self._data_buffer:
        #     res = self._pop_data()
        #     return res if isinstance(res, GamePacket) else None
        # self._get_data()
        # return None

    # @threaded
    # def _get_data(self):
    #     self._busy = True
    #     self._data_buffer.append(self._client.recv())
    #     self._busy = False

    # @threaded
    def send_move(self, move):
        self._client.send_move(move)

    # @threaded
    def send_game(self, game_packet):
        self._client.send_game(game_packet)


def gen_moves(blocks, pos, num_rows=NUM_ROWS, num_cols=NUM_COLS):
    row, col = pos.row, pos.col
    res = []
    for r in [-1, 0, 1]:
        for c in [-1, 0, 1]:
            if -1 < row + r < num_rows and -1 < col + c < num_cols:
                if r == 0 and c == 0:
                    continue
                if blocks[row + r][col + c] != Block_State.UNFOG:
                    res.append(Position(row + r, col + c))
    return res


def do_move(game_state: Game_State, move_pos: Position):
    us_pos = game_state.red_king_pos if game_state.side_to_move == RED else game_state.black_king_pos
    game_state.traces.append(Position(us_pos.row, us_pos.col))
    game_state.blocks[us_pos.row][us_pos.col] = Block_State.UNFOG
    if game_state.side_to_move == RED:
        game_state.red_king_pos = Position(row=move_pos.row, col=move_pos.col)
    else:
        game_state.black_king_pos = Position(row=move_pos.row, col=move_pos.col)
    game_state.side_to_move = -game_state.side_to_move


def undo_move(game_state: Game_State):
    if game_state.side_to_move == RED:
        game_state.black_king_pos = Position(game_state.traces[-1].row, game_state.traces[-1].col)
        game_state.blocks[game_state.black_king_pos.row][game_state.black_king_pos.col] = Block_State.FOG
    else:
        game_state.red_king_pos = Position(game_state.traces[-1].row, game_state.traces[-1].col)
        game_state.blocks[game_state.red_king_pos.row][game_state.red_king_pos.col] = Block_State.FOG
    game_state.traces.pop()
    game_state.side_to_move = -game_state.side_to_move


def eval_state(game_state: Game_State) -> int:
    king_us_pos = game_state.red_king_pos if game_state.side_to_move == RED else game_state.black_king_pos
    king_them_pos = game_state.red_king_pos if game_state.side_to_move == BLACK else game_state.black_king_pos
    if king_us_pos == king_them_pos:
        return LOSS
    moves_us = gen_moves(game_state.blocks, king_us_pos, game_state.num_rows, game_state.num_cols)
    moves_them = gen_moves(game_state.blocks, king_them_pos)
    if len(moves_us) == 0:
        return LOSS
    if len(moves_them) == 0:
        return WIN
    return len(moves_us) - len(moves_them)


class AI(Agent):
    def __init__(self, verbose: bool = False) -> None:
        super().__init__()
        self.type = Agent_Type.AI
        self._thinking = False
        self._move_buffer = []
        self.verbose = verbose

    def gen_moves(self, game_state: Game_State):
        king_us_pos = game_state.red_king_pos if game_state.side_to_move == RED else game_state.black_king_pos
        return gen_moves(game_state.blocks, king_us_pos, game_state.num_rows, game_state.num_cols)

    @property
    def is_thinking(self):
        return self._thinking

    def _pop_move(self):
        return self._move_buffer.pop() if self._move_buffer else None

    def get_move(self, game_state: Game_State):
        if not self.is_thinking:
            return self._pop_move()
        self._make_move(game_state)
        return None

    def get_move_now(self, game_state: Game_State):
        return self.alpha_beta(game_state)

    def _make_move(self, game_state: Game_State):
        self._thinking = True
        self._move_buffer.append(self.alpha_beta(game_state))
        self._thinking = False
    
    def _random_search(self, game_state: Game_State) -> Move:
        moves = self.gen_moves(game_state)
        if moves is not None:
            return Move(game_state.side_to_move, Position(moves[0].row, moves[0].col))
        return None
    
    def negamax(self, game_state: Game_State) -> Move:
        def _minimax(depth, game_state: Game_State, lo, hi):
            opt_val = eval_state(game_state)
            if depth == 0 or opt_val == LOSS or opt_val == WIN:
                return (opt_val, [])
            moves = self.gen_moves(game_state)
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
        
        if game_state.king_them_pos is None:
            opt_val, opt_move = LOSS, None
            last_pos = game_state.traces[-1]
            king_thems = gen_moves(game_state.blocks, last_pos)
            for king_them_pos in king_thems:
                game_state.king_them_pos = king_them_pos
                val, move = _minimax(depth=AI_DEPTH, game_state=game_state, lo=LOSS, hi=WIN)
                game_state.king_them_pos = None
                if val > opt_val:
                    opt_val, opt_move = val, move
        else:
            opt_val, opt_move = _minimax(depth=AI_DEPTH, game_state=game_state, lo=LOSS, hi=WIN)
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

        return Move(game_state.side_to_move, move)


    def alpha_beta(self, game_state: Game_State):
        def _pvs(game_state: Game_State, depth: int, lo: int, hi: int):
            if depth <= 0:
                return (eval_state(game_state), [])
            moves = gen_moves(game_state.blocks, game_state.king_us_pos)
            if not len(moves):
                return (LOSS, [])
            opt_move = moves.pop()
            do_move(game_state, opt_move)
            opt_val, opt_seq = _pvs(game_state, depth - 1, -hi, -lo)
            opt_val = -opt_val
            undo_move(game_state)
            if opt_val > lo:
                if opt_val >= hi:
                    opt_seq.append(opt_move)
                    return (opt_val, opt_seq)
                lo = opt_val

            for move in moves:
                do_move(game_state, move)
                val, seq = _pvs(game_state, depth - 1, -lo - 1, -lo)
                val = -val
                if val > lo and val < hi:
                    val, seq = _pvs(game_state, depth - 1, -hi, -lo)
                    val *= -1
                    if val > lo:
                        lo = val
                        # opt_move = move
                undo_move(game_state)
                if val > opt_val:
                    opt_seq = seq
                    opt_move = move
                    if val >= hi:
                        opt_seq.append(opt_move)
                        return (val, opt_seq)
                    opt_val = val
            opt_seq.append(opt_move)
            return (opt_val, opt_seq)

        def _alpha_beta(game_state: Game_State, depth: int, lo: int, hi: int, lohi: int):
            king_us_pos = game_state.red_king_pos if game_state.side_to_move == RED else game_state.black_king_pos
            king_them_pos = game_state.red_king_pos if game_state.side_to_move == BLACK else game_state.black_king_pos
            if king_them_pos == king_us_pos:
                return (LOSS * lohi, [])
            if depth == 0:
                return (lohi * eval_state(game_state), [])
            moves = self.gen_moves(game_state)
            if len(moves) == 0:
                return (LOSS * lohi, [])
            
            if lohi > 0:
                opt_val, opt_seq = LOSS - 1, []
                for move in moves:
                    do_move(game_state, move)
                    val, seq = _alpha_beta(game_state, depth - 1, lo, hi, -lohi)
                    undo_move(game_state)
                    if val > opt_val or (val == opt_val and len(seq) < len(opt_seq)):
                        seq.append(move)
                        opt_val = val
                        opt_seq = seq
                    lo = max(lo, opt_val)
                    if lo >= hi:
                        return (opt_val, opt_seq)
                return (opt_val, opt_seq)
            else:
                opt_val, opt_seq = WIN + 1, []
                for move in moves:
                    do_move(game_state, move)
                    val, seq = _alpha_beta(game_state, depth - 1, lo, hi, -lohi)
                    undo_move(game_state)
                    if val < opt_val or (val == opt_val and len(seq) < len(opt_seq)):
                        seq.append(move)
                        opt_val = val
                        opt_seq = seq
                    hi = min(hi, opt_val)
                    if lo >= hi:
                        return (opt_val, opt_seq)
                return (opt_val, opt_seq)

        opt_val, opt_move = _alpha_beta(game_state, AI_DEPTH, LOSS, WIN, 1)
        # opt_val, opt_move = _pvs(game_state, AI_DEPTH, LOSS, WIN)
        if opt_move:
            opt_move = opt_move[::-1]
            move = Position(opt_move[0].row, opt_move[0].col)
        else:
            move = gen_moves(game_state.blocks, game_state.king_us_pos)[0]
            move = Position(move.row, move.col)
        if opt_val == WIN and self.verbose:
            print('win')
            l = min(8, len(opt_move))
            print(opt_move[:l])
        if opt_val == LOSS and self.verbose:
            print('lose')
            l = min(8, len(opt_move))
            print(opt_move[:l])

        return Move(game_state.side_to_move, move)
