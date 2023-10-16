"""
 * Copyright (c) [2023] Minh v. Duong; dvminh82@gmail.com
 *
 * You are free to use, modify, re-distribute this code at your own risk
 */
"""
import pygame

from .configs import *
from .base import Block_State, Position, Move, Move_Type
from .game_controller import KingGameController


class KingGameView:
    def __init__(self, game_mode, game_type, network, scr_width=SCR_WIDTH, scr_height=SCR_HEIGHT) -> None:
        pygame.init()
        self.scr_width = scr_width
        self.scr_height = scr_height
        self.network = Game_Network(network)
        self.screen = pygame.display.set_mode((scr_width, scr_height))
        self.title = 'King_Catch'
        if self.network == Game_Network.client:
            self.title += '_client'
        elif self.network == Game_Network.server:
            self.title += '_server'
        pygame.display.set_caption('King_Catch')

        self.cursor = Position(0, 0)
        self._move_buffer = []

        self.game_controller = KingGameController(self, game_mode, game_type, network)

    def game_loop(self):
        while True:
            self.handle_input()
            self.render()
            self.game_controller.play()

    def handle_input(self):
        game = self.game_controller.game
        num_rows, num_cols = game.board.num_rows, game.board.num_cols
        human_turn = self.player.type == Agent_Type.HUMAN
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.cursor.row = (self.cursor.row + num_rows - 1) % num_rows
                elif event.key == pygame.K_DOWN:
                    self.cursor.row = (self.cursor.row + 1) % num_rows
                elif event.key == pygame.K_LEFT:
                    self.cursor.col = (self.cursor.col + num_cols - 1) % num_cols
                elif event.key == pygame.K_RIGHT:
                    self.cursor.col = (self.cursor.col + 1) % num_cols
                elif event.key == pygame.K_RETURN and human_turn:
                    move = Move(side=game.side_to_move, pos=self.cursor)
                    if game.check_move(move) != Move_Type.INVALID:
                        self._move_buffer.append(move)

    def render(self):
        game = self.game_controller.game
        blocks, game_type = game.board.blocks, game.game_type
        num_rows, num_cols = game.board.num_rows, game.board.num_cols
        wsz, hsz = self.scr_height // num_cols, self.scr_width // num_rows
        rk, bk = game.board.red_king_pos, game.board.black_king_pos

        for r in range(num_rows):
            for c in range(num_cols):
                color = (50, 100, 100) if blocks[r][c].state == Block_State.UNFOG else (125, 125, 125)
                pygame.draw.rect(self.screen, color, (c * wsz, r * hsz, hsz, wsz))
        if game_type == Game_Type.VISIBLE:
            pygame.draw.rect(self.screen, (255, 10, 20), (rk.col * wsz, rk.row * hsz, hsz, wsz))
            pygame.draw.rect(self.screen, (5, 5, 5), (bk.col * wsz, bk.row * hsz, hsz, wsz))
        elif self.side == RED:
            pygame.draw.rect(self.screen, (255, 10, 20), (rk.col * wsz, rk.row * hsz, hsz, wsz))
        else:
            pygame.draw.rect(self.screen, (5, 5, 5), (bk.col * wsz, bk.row * hsz, hsz, wsz))
        # if self.current_player.type == Agent_Type.HUMAN:
        pygame.draw.rect(self.screen, (255, 192, 203), (self.cursor.col * wsz, self.cursor.row * hsz, hsz, wsz))
        pygame.display.update()

    @property
    def side(self):
        return self.game_controller.side

    @property
    def side_to_move(self):
        return self.game_controller.side_to_move

    @property
    def red_player(self):
        return self.game_controller.red_player
    
    @property
    def black_player(self):
        return self.game_controller.black_player
    
    @property
    def player(self):
        return self.red_player if self.side_to_move == RED else self.black_player

    def get_move(self):
        return self._move_buffer.pop() if self._move_buffer else None

    def game_over(self, win_side: int):
        print('Game won!')
        self.reset()

    def reset(self):
        self.cursor = Position(0, 0)

    def quit(self):
        pygame.quit()
        exit()