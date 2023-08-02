import time
from threading import Thread, Event

import pygame

from .game import Game
from .configs import *
from .utils import rc_2_pos
from .base import Block_State, Position, Move, Move_Type
from .clock import TimeControl


ev = Event()
ev.set()


def _ai_move(kg):
    ev.clear()
    game, side_to_move = kg.game, kg.game.side_to_move
    player = game.red_player if game.side_to_move == RED else game.black_player
    kg.ai_is_thinking = True
    kg.ai_return_move = None
    game_state = game.get_state()
    time.sleep(1)
    kg.ai_return_move = player.make_move(game_state, side_to_move)
    kg.ai_is_thinking = False


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
        self.ai_is_thinking = False
        self.ai_return_move = None
        self.time_control = TimeControl(total_time=GAME_TIME, inc_per_move=2, num_players=2)

    def play(self):
        self.render()
        pygame.display.update()
        win_side = None
        while True:
            self.time_control.tick()
            if self.time_control.is_time_over:
                win_side = -self.game.side_to_move
                break
            move = None
            player = self.game.red_player if self.game.side_to_move == RED else self.game.black_player
            if player.type == Agent_Type.AI and ev.is_set() and not self.ai_is_thinking:
                bg_thread = Thread(target=_ai_move, args=(self,))
                bg_thread.setDaemon(True)
                bg_thread.start()
            
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
                    elif event.key == pygame.K_RETURN and self.game.is_human_turn:
                        move = Move(side=self.game.side_to_move, pos=self.cursor)
            if not self.game.is_human_turn and not self.ai_is_thinking:
                move = self.ai_return_move
            if move is not None:
                m = self.game.make_move(move)
                if m != Move_Type.INVALID:
                    self.time_control.move()
                    ev.set()
                if m == Move_Type.WIN:
                    win_side = -self.game.side_to_move
                    break
            self.render()
            pygame.display.update()
        self.game_over(win_side=win_side)
            
    def reset(self):
        self.game.reset()
        self.time_control.reset()
        self.play()

    def quit(self):
        if self.game is not None:
            del self.game
        pygame.quit()
        exit()

    def render(self):
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
        # if self.current_player.type == Agent_Type.HUMAN:
        pygame.draw.rect(self.screen, (255, 192, 203), (self.cursor.col * wsz, self.cursor.row * hsz, hsz, wsz))

    @property
    def current_player(self):
        return self.game.red_player if self.game.side_to_move == RED else self.game.black_player

    def update(self):
        pass

    def game_over(self, win_side: int):
        self.game.game_over(win_side=win_side)
        self.reset()
