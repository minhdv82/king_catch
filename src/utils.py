from typing import Tuple
import random

from .configs import NUM_ROWS


def init_game():
    pass


def rc_2_pos(row: int, col: int, nr=NUM_ROWS) -> int:
    return row + col * nr


def pos_2_rc(pos: int, nr=NUM_ROWS) -> Tuple[int, int]:
    row = pos % nr
    col = pos // nr
    return tuple(row, col)
