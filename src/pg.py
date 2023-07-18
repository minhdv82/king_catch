import time
import pygame

from .game import Game
from .configs import *
from .utils import rc_2_pos
from .base import Block_State, Position, Move, Move_Type


class KingGame:
    def __init__(self, game: Game=None) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((SCR_WIDTH, SCR_HEIGHT))
        pygame.display.set_caption('King_Catch')

        if game is not None:
            self.game = game
        else:
            self.game = Game()

        self.cursor = Position(0, 0)

    def play(self):
        self.draw()
        pygame.display.update()
        win_side = None
        while True:
            if self.game.board.check_lose(self.game.side_to_move):
                win_side =  -self.game.side_to_move
                break
            move = None
            player = self.game.red_player if self.game.side_to_move == RED else self.game.black_player
            if player.type == Agent_Type.AI:
                game_state = self.game.board.get_state(game_type=self.game.game_type)
                move = player.make_move(game_state, self.game.side_to_move)
                time.sleep(1)
            else:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.quit()
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_UP:
                            self.cursor.row = (self.cursor.row + NUM_ROWS - 1) % NUM_ROWS
                        elif event.key == pygame.K_DOWN:
                            self.cursor.row = (self.cursor.row + 1) % NUM_ROWS
                        elif event.key == pygame.K_LEFT:
                            self.cursor.col = (self.cursor.col + NUM_COLS - 1) % NUM_COLS
                        elif event.key == pygame.K_RIGHT:
                            self.cursor.col = (self.cursor.col + 1) % NUM_COLS
                        elif event.key == pygame.K_RETURN:       
                            move = Move(side=self.game.side_to_move, pos=self.cursor)
            if move is not None:
                m = self.game.make_move(move)
                if m == Move_Type.WIN:
                    win_side = -self.game.side_to_move
                    break
            self.draw()
            pygame.display.update()
        self.game_over(win_side=win_side)
            
    def reset(self):
        self.game.reset()
        self.play()

    def quit(self):
        # self.game.quit()
        pygame.quit()
        exit()

    def draw(self):
        blocks = self.game.board.blocks
        wsz, hsz = SCR_WIDTH // NUM_COLS, SCR_HEIGHT // NUM_ROWS
        for r in range(NUM_ROWS):
            for c in range(NUM_COLS):
                color = (50, 100, 100) if blocks[rc_2_pos(r, c)].state == Block_State.UNFOG else (125, 125, 125)
                pygame.draw.rect(self.screen, color, (c * wsz, r * hsz, hsz, wsz))
        if self.game.game_type == Game_Type.VISIBLE or (self.game.side_to_move == RED and self.game.red_player.type == Agent_Type.HUMAN):
            pygame.draw.rect(self.screen, (255, 10, 20), (self.game.board.red_king_pos.col * wsz, self.game.board.red_king_pos.row * hsz, hsz, wsz))
        if self.game.game_type == Game_Type.VISIBLE or (self.game.side_to_move == BLACK and self.game.black_player.type == Agent_Type.HUMAN):
            pygame.draw.rect(self.screen, (5, 5, 5), (self.game.board.black_king_pos.col * wsz, self.game.board.black_king_pos.row * hsz, hsz, wsz))
        if self.game.game_mode != Game_Mode.AI_VS_AI:
            pygame.draw.rect(self.screen, (255, 192, 203), (self.cursor.col * wsz, self.cursor.row * hsz, hsz, wsz))

    def update(self):
        pass

    def game_over(self, win_side: int):
        self.game.game_over(win_side=win_side)
        self.reset()
