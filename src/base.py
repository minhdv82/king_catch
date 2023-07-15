from enum import Enum
from dataclasses import dataclass

from .configs import *
from .utils import rc_2_pos


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
    

class Board:
    def __init__(self, red_king_pos: Position, black_king_pos: Position, side_to_move: int=RED) -> None:
        self.blocks = [Block] * NUM_BLOCKS
        self.red_king_pos, self.black_king_pos = red_king_pos, black_king_pos
        self.side_to_move = side_to_move
        self.reset()

    def reset(self, red_king_pos: Position=None, black_king_pos: Position=None, side_to_move: int=RED) -> None:
        for row in range(NUM_ROWS):
            for col in range(NUM_COLS):
                pos = rc_2_pos(row, col)
                block = Block(Block_State.FOG, Position(row=row, col=col))
                self.blocks[pos] = block
        if red_king_pos is not None:
            self.red_king_pos = red_king_pos
        if black_king_pos is not None:
            self.black_king_pos = black_king_pos
        self.side_to_move = side_to_move

    def switch_side(self):
        self.side_to_move = 1 - self.side_to_move

    def count_move(self, position: Position) -> int:
        res = 0
        row, col = position.row, position.col
        cur_pos = rc_2_pos(row, col)
        for r in [-1, 0, 1]:
            for c in [-1, 0, 1]:
                if -1 < row + r < NUM_ROWS and -1 < col + c < NUM_COLS:
                    pos = rc_2_pos(row + r, col + c)
                    if pos == cur_pos:
                        continue
                    if self.blocks[pos].state != Block_State.UNFOG:
                        res += 1
        return res

    def check_lose(self, side: int) -> bool:
        pos = self.red_king_pos if side == RED else self.black_king_pos
        return self.count_move(pos) == 0

    def check_board(self, pos: Position) -> bool:
        row, col = pos.row, pos.col
        return -1 < row < NUM_ROWS and -1 < col < NUM_COLS

    def distance(self, p: Position, q: Position) -> int:
        return (p.row - q.row)**2 + (p.col - q.col)**2

    def check_move(self, move: Move) -> Move_Type:
        side, pos = move.side, move.pos
        if side != self.side_to_move or self.blocks[rc_2_pos(pos.row, pos.col)].state == Block_State.UNFOG:
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
            self.blocks[rc_2_pos(king_pos.row, king_pos.col)].state = Block_State.UNFOG
            if verbose:
                print('King moves from {} {} to {} {}'.format(king_pos.row, king_pos.col, move.pos.row, move.pos.col))
            king_pos.row, king_pos.col = move.pos.row, move.pos.col
            self.switch_side()
            if self.check_lose(self.side_to_move):
                m = Move_Type.WIN
        elif verbose:
            print('Invalid move!')
        return m

    def draw(self):
        red_king_pos, black_king_pos = self.red_king_pos, self.black_king_pos
        rp, bp = rc_2_pos(red_king_pos.row, red_king_pos.col), rc_2_pos(black_king_pos.row, black_king_pos.col)
        for row in range(NUM_ROWS):
            for col in range(NUM_COLS):
                pos = rc_2_pos(row, col)
                if pos == rp:
                    print(' K ', end='')
                elif pos == bp:
                    print(' k ', end='')
                elif self.blocks[pos].state == Block_State.FOG:
                    print(' * ', end='')
                else:
                    print(' - ', end='')
            print('')
        print('')
