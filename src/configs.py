"""
 * Copyright (c) [2023] Minh v. Duong; dvminh82@gmail.com
 *
 * You are free to use, modify, re-distribute this code at your own risk
 */
"""
from enum import Enum

RED, BLACK, KIBITZ = 1, -1, 0
RED_WIN, BLACK_WIN = 0, 1
NUM_ROWS, NUM_COLS = 8, 8
NUM_BLOCKS = NUM_ROWS * NUM_COLS

SCR_WIDTH, SCR_HEIGHT = 600, 600
FOG_COLOR = 'Brown'
UNFOG_COLOR = 'Blue'
SEC_TO_TICKS, GAME_TIME = 60, 3600
AI_DEPTH = 20

class Game_Mode(Enum):
    MAN_VS_MAN = 0
    MAN_VS_AI = 1
    AI_VS_AI = 2


class Game_Type(Enum):
    VISIBLE = 0
    INVISIBLE = 1


class Agent_Type(Enum):
    AI = 0
    HUMAN = 1
    BOT = 2


class Game_Network(Enum):
    offline = 0
    server = 1
    client = 2


# class Game_Side(Enum):
#     KIBITZ = 0
#     RED = 1
#     BLACK = -1