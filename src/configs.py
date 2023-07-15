from enum import Enum

AI, HUMAN = 0, 1
RED, BLACK = 0, 1
RED_WIN, BLACK_WIN = 0, 1
NUM_ROWS, NUM_COLS = 8, 8
NUM_BLOCKS = NUM_ROWS * NUM_COLS

SCR_WIDTH, SCR_HEIGHT = 800, 800
FOG_COLOR = 'Brown'
UNFOG_COLOR = 'Blue'

class Game_Mode(Enum):
    MAN_VS_MAN = 0
    MAN_VS_AI = 1
    AI_VS_AI = 2
