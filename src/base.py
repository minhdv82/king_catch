"""
 * Copyright (c) [2023] Minh v. Duong; dvminh82@gmail.com
 *
 * You are free to use, modify, re-distribute this code at your own risk
 */
"""
from typing import List
from enum import Enum
from dataclasses import dataclass

from .configs import *
# from .utils import rc_2_pos


@dataclass
class Position:
    row: int
    col: int
    def __eq__(self, rhs: object) -> bool:
        return self.row == rhs.row and self.col == rhs.col

@dataclass
class Move:
    side: int
    pos: Position


class Block_State(Enum):
    RED = 0
    BLACK = 1
    FOG = 2
    UNFOG = 3


class Move_Type(Enum):
    INVALID = 0
    VALID = 1
    WIN = 2
    LOSE = 3


class Block:
    def __init__(self, state: Block_State, position: Position) -> None:
        self.state = state
        self.position = position


@dataclass
class Game_State:
    blocks: List[List[Block_State]]
    traces: List[Position]
    king_us_pos: Position
    king_them_pos: Position
    num_rows: int=NUM_ROWS
    num_cols: int=NUM_COLS


class Board:
    def __init__(self, num_rows: int=NUM_ROWS, num_cols: int=NUM_COLS, red_king_pos: Position = None, black_king_pos: Position = None,
                 side_to_move: int=RED, blocks: List[Block]=None) -> None:
        self.num_rows = num_rows
        self.num_cols = num_cols
        self.num_blocks = self.num_rows * self.num_cols
        self.traces = []
        self.red_king_pos = red_king_pos
        self.black_king_pos = black_king_pos
        self.side_to_move = side_to_move
        if blocks is None:
            self.blocks = [[Block] * self.num_cols for _ in range(self.num_rows)]
            self.reset(red_king_pos, black_king_pos)
        else:
            self.blocks = blocks

    def reset(self, red_king_pos, black_king_pos) -> None:
        for row in range(self.num_rows):
            for col in range(self.num_cols):
                block = Block(Block_State.FOG, Position(row=row, col=col))
                self.blocks[row][col] = block
        self.red_king_pos = red_king_pos
        self.black_king_pos = black_king_pos

    def switch_side(self):
        self.side_to_move = -self.side_to_move

    def count_move(self, position: Position) -> int:
        res = 0
        row, col = position.row, position.col
        for r in [-1, 0, 1]:
            for c in [-1, 0, 1]:
                if -1 < row + r < self.num_rows and -1 < col + c < self.num_cols:
                    if r == 0 and c == 0:
                        continue
                    if self.blocks[row + r][col + c].state != Block_State.UNFOG:
                        res += 1
        return res

    def get_moves(self, side_to_move: int):
        res = []
        king_pos = self.red_king_pos if side_to_move == RED else self.black_king_pos
        row, col = king_pos.row, king_pos.col
        for r in [-1, 0, 1]:
            for c in [-1, 0, 1]:
                if -1 < row + r < self.num_rows and -1 < col + c < NUM_COLS:
                    if r == 0 and c == 0:
                        continue
                    if self.blocks[row + r][col + c].state != Block_State.UNFOG:
                        res.append(Position(row + r, col + c))
        return res

    def check_lose(self, side: int) -> bool:
        pos = self.red_king_pos if side == RED else self.black_king_pos
        return self.count_move(pos) == 0

    def check_board(self, pos: Position) -> bool:
        row, col = pos.row, pos.col
        return -1 < row < self.num_rows and -1 < col < self.num_cols

    def distance(self, p: Position, q: Position) -> int:
        return (p.row - q.row)**2 + (p.col - q.col)**2

    def check_move(self, move: Move) -> Move_Type:
        side, pos = move.side, move.pos
        if side != self.side_to_move or self.blocks[pos.row][pos.col].state == Block_State.UNFOG:
            return Move_Type.INVALID
        if side == RED:
            king_us_pos, king_them_pos = self.red_king_pos, self.black_king_pos
        else:
            king_us_pos, king_them_pos = self.black_king_pos, self.red_king_pos

        if not self.check_board(pos) or self.distance(pos, king_us_pos) == 0 or self.distance(pos, king_us_pos) > 2:
            return Move_Type.INVALID
        if pos == king_them_pos:
            return Move_Type.WIN
        return Move_Type.VALID

    def make_move(self, move: Move, verbose=False) -> Move_Type:
        m = self.check_move(move)
        if m != Move_Type.INVALID:
            king_pos = self.red_king_pos if move.side == RED else self.black_king_pos
            self.blocks[king_pos.row][king_pos.col].state = Block_State.UNFOG
            self.traces.append(Position(king_pos.row, king_pos.col))
            if verbose:
                print('King moves from {} {} to {} {}'.format(king_pos.row, king_pos.col, move.pos.row, move.pos.col))
            king_pos.row, king_pos.col = move.pos.row, move.pos.col
            self.switch_side()
            if self.check_lose(self.side_to_move):
                m = Move_Type.WIN
        elif verbose:
            print('Invalid move!')
        return m

    def force_move(self, move: Move, m: Move_Type, verbose: bool=False):
        king_pos = self.red_king_pos if move.side == RED else self.black_king_pos
        if king_pos is None:
            self.blocks[move.pos.row][move.pos.col].state = Block_State.UNFOG
            self.traces.append(Position(move.pos.row, move.pos.col))
        else:
            self.blocks[king_pos.row][king_pos.col].state = Block_State.UNFOG
            self.traces.append(Position(king_pos.row, king_pos.col))
            if verbose:
                print('King moves from {} {} to {} {}'.format(king_pos.row, king_pos.col, move.pos.row, move.pos.col))
            king_pos.row, king_pos.col = move.pos.row, move.pos.col

        self.switch_side()
        return m

    def draw(self):
        red_king_pos, black_king_pos = self.red_king_pos, self.black_king_pos
        for row in range(self.num_rows):
            for col in range(self.self.num_cols):
                pos = Position(row, col)
                if pos == red_king_pos:
                    print(' K ', end='')
                elif pos == black_king_pos:
                    print(' k ', end='')
                elif self.blocks[row][col].state == Block_State.FOG:
                    print(' * ', end='')
                else:
                    print(' - ', end='')
            print('')
        print('')

    def get_state(self, game_type=Game_Type.VISIBLE):
        king_us_pos = Position(self.red_king_pos.row, self.red_king_pos.col) if self.side_to_move == RED else \
              Position(self.black_king_pos.row, self.black_king_pos.col)
        if game_type == Game_Type.VISIBLE:
            king_them_pos = Position(self.black_king_pos.row, self.black_king_pos.col) if self.side_to_move == RED else \
                Position(self.red_king_pos.row, self.red_king_pos.col)
        else:
            king_them_pos = None
        blks = []
        trs = []
        for block in self.blocks:
            blks.append(block.state)
        for trace in self.traces:
            trs.append(Position(trace.row, trace.col))

        return Game_State(blocks=blks, traces=trs, king_us_pos=king_us_pos, king_them_pos=king_them_pos,
                          num_rows=self.num_rows, num_cols=self.num_cols)
