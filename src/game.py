
from .configs import *
from .base import *
from .agent import *


class Game:
    def __init__(self, board: Board=None, side_to_move=RED, game_mode: Game_Mode=Game_Mode.MAN_VS_MAN) -> None:
        self.game_mode = game_mode
        self.side_to_move = side_to_move
        self.red_wins = 0
        self.black_wins = 0
        self.red_player = None
        self.black_player = None
        if board is not None:
            self.board = board
        else:
            red_king_pos, black_king_pos = self.random_kings()
            self.board = Board(red_king_pos=red_king_pos, black_king_pos=black_king_pos)
        self.init_players()

    def init_players(self):
        if self.game_mode == Game_Mode.MAN_VS_MAN:
            self.red_player = Human()
            self.black_player = Human()
        elif self.game_mode == Game_Mode.AI_VS_AI:
            self.red_player = AI()
            self.black_player = AI()
        else:
            self.red_player = Human()
            self.black_player = AI()

    def reset(self) -> None:
        self.side_to_move = RED
        red_king_pos, black_king_pos = self.random_kings()
        self.board.reset(red_king_pos=red_king_pos, black_king_pos=black_king_pos)
        self.play()

    def move(self, move: Move) -> None:
        m = self.board.make_move(move)
        self.board.draw()
        if m == Move_Type.WIN:
            self.game_over(win_side=move.side)
        elif m == Move_Type.VALID:
            self.side_to_move = 1 - self.side_to_move
    
    @staticmethod
    def random_kings():
        import random
        while True:
            red_row, black_row = random.randint(0, NUM_ROWS), random.randint(0, NUM_ROWS)
            red_col, black_col = random.randint(0, NUM_COLS), random.randint(0, NUM_COLS)
            if red_row != black_row or red_col != black_col:
                red_king_pos, black_king_pos = Position(red_row, red_col), Position(black_row, black_col)
                return (red_king_pos, black_king_pos)
            
    def game_over(self, win_side: int) -> None:
        if win_side == RED:
            self.red_wins += 1
        else:
            self.black_wins += 1

        self.reset()

    def play(self):
        while True:
            if self.side_to_move == RED:
                self.red_player.make_move(self.board, self.side_to_move)
            else:
                self.black_player.make_move(self.board, self.side_to_move)
