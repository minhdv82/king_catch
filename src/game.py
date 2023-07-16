
from .configs import *
from .base import *
from .agent import *


class Game:
    def __init__(self, board: Board=None, side_to_move=RED, game_mode=Game_Mode.MAN_VS_AI, game_type=Game_Type.VISIBLE) -> None:
        self.game_mode = game_mode
        self.game_type = game_type
        self.side_to_move = side_to_move
        self.games_played = 1
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
    
    @staticmethod
    def random_kings():
        import random
        while True:
            red_row, black_row = random.randint(0, NUM_ROWS - 1), random.randint(0, NUM_ROWS - 1)
            red_col, black_col = random.randint(0, NUM_COLS - 1), random.randint(0, NUM_COLS - 1)
            if red_row != black_row or red_col != black_col:
                red_king_pos, black_king_pos = Position(red_row, red_col), Position(black_row, black_col)
                return (red_king_pos, black_king_pos)
            
    def game_over(self, win_side: int) -> None:
        if win_side == RED:
            print('Red has won the game!')
            self.red_wins += 1
        else:
            print('Black has won the game!')
            self.black_wins += 1
        self.games_played += 1
        self.reset()

    def switch_side(self):
        self.side_to_move = 1 - self.side_to_move

    def make_move(self, move: Move) -> Move_Type:
        m = self.board.make_move(move)
        if m != Move_Type.INVALID:
            self.switch_side()
        return m

    def play(self):
        win_side = None
        print('Game number {}:'.format(self.games_played))
        while True:
            self.board.draw()
            if self.board.check_lose(self.side_to_move):
                win_side = 1 - self.side_to_move
                break
            if self.side_to_move == RED:
                move = self.red_player.make_move(self.board, self.side_to_move)
            else:
                move = self.black_player.make_move(self.board, self.side_to_move)
            m = self.board.make_move(move)
            if m == Move_Type.WIN:
                win_side = self.side_to_move
                break
            else:
                self.side_to_move = 1 - self.side_to_move
        self.game_over(win_side=win_side)
