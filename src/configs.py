from enum import Enum

RED, BLACK = 1, -1
RED_WIN, BLACK_WIN = 0, 1
NUM_ROWS, NUM_COLS = 6, 6
NUM_BLOCKS = NUM_ROWS * NUM_COLS

SCR_WIDTH, SCR_HEIGHT = 600, 600
FOG_COLOR = 'Brown'
UNFOG_COLOR = 'Blue'
SEC_TO_TICKS, GAME_TIME = 60, 30
AI_DEPTH = 10

class Game_Mode(Enum):
    MAN_VS_MAN = 0
    MAN_VS_AI = 1
    AI_VS_AI = 2


class Game_Type(Enum):
    INVISIBLE = 0
    VISIBLE = 1


class Agent_Type(Enum):
    AI = 0
    HUMAN = 1
