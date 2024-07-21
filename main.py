import sys
import os
import pickle
import copy
import math as mp
import random
from constants import *

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "1"
import pygame as pg

pg.init()

screen = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption('Tic Tac Toe')

base_dir = os.path.dirname(__file__)

ICON = pg.image.load(os.path.join(base_dir, ICON_FILE))
pg.display.set_icon(ICON)

clock = pg.time.Clock()

CLICK_SOUND = pg.mixer.Sound(os.path.join(base_dir, CLICK_SOUND_FILE))
WIN_SOUND = pg.mixer.Sound(os.path.join(base_dir, WIN_SOUND_FILE))


class AI:

    def __init__(self, board, ai_mode, ai_player):  # Game Modes available : 'random' and 'minimax'

        self.board = board
        self.mode = ai_mode
        self.ai_player = ai_player
        self.opponent_player = self.get_other_player()

    def get_other_player(self):

        players = [1, 2]
        players.remove(self.ai_player)
        return players[0]

    def minimax(self, board, max_or_min='max'):  # ai is maximising

        case = board.state()

        if case == self.ai_player:
            return (1, None)

        elif case == self.opponent_player:
            return (-1, None)

        elif board.isfull() and case == 0:
            return (0, None)

        if max_or_min == 'min':

            min_eval = 100
            best_move = None
            empty_squares = board.get_empty_squares()

            for row, col in empty_squares:

                temporary_board = copy.deepcopy(board)
                temporary_board.mark_move(row, col, self.opponent_player)

                eval = self.minimax(temporary_board, 'max')[0]

                if eval == -1:

                    min_eval = eval
                    best_move = (row, col)

                    return (min_eval, best_move)

                elif eval < min_eval:

                    min_eval = eval
                    best_move = (row, col)

            return (min_eval, best_move)

        elif max_or_min == 'max':

            max_eval = -100
            best_move = None
            empty_squares = board.get_empty_squares()

            for row, col in empty_squares:

                temporary_board = copy.deepcopy(board)
                temporary_board.mark_move(row, col, self.ai_player)

                eval = self.minimax(temporary_board, 'min')[0]

                if eval == 1:

                    max_eval = eval
                    best_move = (row, col)

                    return (max_eval, best_move)

                elif eval > max_eval:

                    max_eval = eval
                    best_move = (row, col)

            return (max_eval, best_move)

        raise Exception('The board not found in any case')

    def ai_move(self):

        if self.mode == 'random':

            empty_squares = self.board.get_empty_squares()
            pos = random.choice(empty_squares)

        elif self.mode == 'minimax':

            eval, pos = self.minimax(self.board)

        return pos


class Board:

    def __init__(self):

        self.board = [[0 for i in range(COLS)] for j in range(ROWS)]
        self.marked_squares = 0

    def state(self, return_positions=False):

        """
        :return: 0 if no winner yet
        :return: 1 if player 1 wins
        :return: 2 if player 2 wins
        """

        # check horizontal
        for row in range(ROWS):
            if all([self.board[row][0] == self.board[row][col] != 0 for col in range(COLS)]):

                if return_positions:
                    return (self.board[row][0], 'horizontal', (row, 0), (row, COLS - 1))

                return self.board[row][0]

        # check for vertical
        for col in range(COLS):
            if all([self.board[0][col] == self.board[row][col] != 0 for row in range(ROWS)]):

                if return_positions:
                    return (self.board[0][col], 'vertical', (0, col), (ROWS - 1, col))

                return self.board[0][col]

        # check for diagonal
        if all([self.board[0][0] == self.board[i][i] != 0 for i in range(ROWS)]):

            if return_positions:
                return (self.board[0][0], 'down diagonal', (0, 0), (ROWS - 1, COLS - 1))

            return self.board[0][0]

        if all([self.board[0][COLS - 1] == self.board[i][COLS - i - 1] != 0 for i in range(ROWS)]):

            if return_positions:
                return (self.board[0][COLS - 1], 'up diagonal', (ROWS - 1, 0), (0, COLS - 1))

            return self.board[0][COLS - 1]

        # no win yet
        return 0

    def mark_move(self, row, col, player):

        self.board[row][col] = player
        self.marked_squares += 1

    def check_empty(self, row, col):
        return self.board[row][col] == 0

    def get_empty_squares(self):

        empty_squares = []

        for row in range(ROWS):
            for col in range(COLS):

                if self.check_empty(row, col):
                    empty_squares.append((row, col))

        return empty_squares

    def isfull(self):
        return self.marked_squares == ROWS * COLS


class Game:

    def __init__(self):

        self.cur_player = 1
        self.game_mode = None  # Options : 'pvp' or 'ai'

        self.running = True

    def make_move(self, row, col):

        self.board.mark_move(row, col, self.cur_player)
        self.draw_fig(row, col)
        self.next_turn()

    def next_turn(self):

        players = [1, 2]
        players.remove(self.cur_player)
        self.cur_player = players[0]

    def game_over(self):

        game_over = False
        state_details = self.board.state(return_positions=True)

        if state_details != 0:
            game_over = True
            winner_player, orientation, first_element, last_element = state_details
            self.final_state = winner_player
            self.show_win(winner_player, orientation, first_element, last_element)

        elif self.board.isfull() and state_details == 0:
            self.final_state = 0
            game_over = True

        return game_over

    def initialize_game(self):

        with open(os.path.join(base_dir, DATA_FILE), 'rb') as f:
            data = pickle.load(f)

        self.game_mode = data['game mode']
        self.board = Board()

        if self.game_mode == 'ai':
            ai_mode = data['ai mode']
            ai_player = data['ai player']

            self.ai = AI(self.board, ai_mode, ai_player)

        screen.fill(BG_COLOR)
        self.draw_lines()

    def start_screen(self):
        # Buttons
        if BUTTON_BORDER:
            button_border = (BUTTON_BORDER_WIDTH, BUTTON_BORDER_COLOR)
        else:
            button_border = False

        if BUTTON_HOVER:
            button_hover = (HOVER_COLOR, HOVER_TEXT_COLOR)
        else:
            hover_color = False

        button_font = BUTTON_FONT_NAME, BUTTON_FONT_SIZE, BUTTON_FONT_COLOR, True, False

        def computer_mode_selection():

            # Buttons
            hard_mode_button = Button('Hard', BUTTON_SIZE, (round(WIDTH / 2), self.scale_value(320)))
            easy_mode_button = Button('Easy', BUTTON_SIZE, (round(WIDTH / 2), self.scale_value(220)))

            run = True
            while run:

                clock.tick(FPS)
                screen.fill(BG_COLOR)

                # Displaying
                hard_mode_button.blit(button_font, BUTTON_COLOR, button_border, button_hover)
                easy_mode_button.blit(button_font, BUTTON_COLOR, button_border, button_hover)

                for event in pg.event.get():

                    if event.type == pg.QUIT:
                        pg.quit()
                        sys.exit()
                        break

                    if event.type == pg.MOUSEBUTTONDOWN and event.button == 1 and hard_mode_button.check_click():
                        Button.remove_all_buttons()
                        CLICK_SOUND.play()

                        data = {'game mode': 'ai', 'ai mode': 'minimax', 'ai player': 2}
                        run = False

                    if event.type == pg.MOUSEBUTTONDOWN and event.button == 1 and easy_mode_button.check_click():
                        Button.remove_all_buttons()
                        CLICK_SOUND.play()

                        data = {'game mode': 'ai', 'ai mode': 'random', 'ai player': 2}
                        run = False

                pg.display.update()

            return data

        def shortcuts_selections():

            # Button
            back_button = Button('Back', BUTTON_SIZE, (self.scale_value(400), self.scale_value(495)))

            text = '''
P : To play multiplayer
H : To play with Computer - Hard
E : To play with Computer - Easy
S : To go to Shortcuts
Q : To quit

ENTER : To restart Game 
M     : To go to Main Menu'''

            lines = text.split('\n')

            text_font = pg.font.SysFont(NORMAL_FONT_NAME, NORMAL_FONT_SIZE)
            line_height = 10

            run = True
            while run:

                clock.tick(FPS)
                screen.fill(BG_COLOR)

                back_button.blit(button_font, BUTTON_COLOR, button_border, button_hover)

                x, y = (self.scale_value(30), self.scale_value(15))

                for line in lines:
                    text_render = text_font.render(line, 1, NORMAL_FONT_COLOR)
                    screen.blit(text_render, (x, y))

                    text_height = text_render.get_height()
                    y += text_height + line_height

                for event in pg.event.get():

                    if event.type == pg.QUIT:

                        pg.quit()
                        sys.exit()
                        run = False

                    elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1 and back_button.check_click():

                        Button.remove_all_buttons()
                        CLICK_SOUND.play()

                        self.start_screen()
                        run = False

                pg.display.update()

        # Header
        header_pos = (round(WIDTH / 2), self.scale_value(75))
        header_font = pg.font.SysFont(HEADER_FONT_NAME, HEADER_FONT_SIZE, bold=True)

        header_render = header_font.render('TIC TAC TOE', 1, HEADER_FONT_COLOR)
        header_text_rect = header_render.get_rect(center=header_pos)

        # Buttons

        multiplayer_button = Button('Multiplayer', BUTTON_SIZE, (round(WIDTH / 2), self.scale_value(175)))
        computer_button = Button('Computer', BUTTON_SIZE, (round(WIDTH / 2), self.scale_value(275)))
        shortcuts_button = Button('Shortcuts', BUTTON_SIZE, (round(WIDTH / 2), self.scale_value(375)))
        quit_button = Button('Quit', BUTTON_SIZE, (round(WIDTH / 2), self.scale_value(475)))

        run = True
        while run:

            clock.tick(FPS)
            screen.fill(BG_COLOR)

            # Displaying

            screen.blit(header_render, header_text_rect.topleft)
            multiplayer_button.blit(button_font, BUTTON_COLOR, button_border, button_hover)
            computer_button.blit(button_font, BUTTON_COLOR, button_border, button_hover)
            shortcuts_button.blit(button_font, BUTTON_COLOR, button_border, button_hover)
            quit_button.blit(button_font, BUTTON_COLOR, button_border, button_hover)

            for event in pg.event.get():

                if ((event.type == pg.KEYDOWN and event.key == pg.K_p) or
                        (event.type == pg.MOUSEBUTTONDOWN and event.button == 1 and multiplayer_button.check_click())):

                    Button.remove_all_buttons()
                    CLICK_SOUND.play()

                    data = {'game mode': 'pvp', 'ai mode': None, 'ai player': None}
                    self.set_game_data(data)
                    run = False

                elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1 and computer_button.check_click():

                    Button.remove_all_buttons()
                    CLICK_SOUND.play()

                    data = computer_mode_selection()
                    self.set_game_data(data)
                    run = False

                elif event.type == pg.KEYDOWN and event.key == pg.K_h:

                    Button.remove_all_buttons()
                    CLICK_SOUND.play()

                    data = {'game mode': 'ai', 'ai mode': 'minimax', 'ai player': 2}
                    self.set_game_data(data)
                    run = False

                elif event.type == pg.KEYDOWN and event.key == pg.K_e:

                    Button.remove_all_buttons()
                    CLICK_SOUND.play()

                    data = {'game mode': 'ai', 'ai mode': 'random', 'ai player': 2}
                    self.set_game_data(data)
                    run = False

                elif ((event.type == pg.KEYDOWN and event.key == pg.K_s) or
                      (event.type == pg.MOUSEBUTTONDOWN and event.button == 1 and shortcuts_button.check_click())):

                    Button.remove_all_buttons()
                    CLICK_SOUND.play()

                    shortcuts_selections()
                    run = False

                elif ((event.type == pg.QUIT) or (event.type == pg.KEYDOWN and event.key == pg.K_q) or
                      (event.type == pg.MOUSEBUTTONDOWN and event.button == 1 and quit_button.check_click())):

                    pg.quit()
                    sys.exit()
                    run = False

            pg.display.update()

    def end_screen(self):

        # Surface
        surface = pg.Surface(screen.get_size()).convert_alpha()
        surface.set_alpha(20)
        surface.fill(BG_COLOR)

        # Header
        header_font_size = HEADER_FONT_SIZE

        if self.final_state == 0:
            header_text = 'DRAW'

        elif self.game_mode == 'pvp':

            if self.final_state == 1:
                header_text = 'X WON'

            elif self.final_state == 2:
                header_text = 'O WON'

        elif self.game_mode == 'ai':

            if self.final_state == self.ai.ai_player:
                header_text = 'COMPUTER WON'
                header_font_size = 50

            else:
                header_text = 'YOU WON'

        header_pos = (round(WIDTH / 2), self.scale_value(100))
        header_font = pg.font.SysFont(HEADER_FONT_NAME, header_font_size, bold=True)

        header_render = header_font.render(header_text, 1, HEADER_FONT_COLOR)
        header_text_rect = header_render.get_rect(center=header_pos)

        # Buttons
        if BUTTON_BORDER:
            button_border = (BUTTON_BORDER_WIDTH, BUTTON_BORDER_COLOR)
        else:
            button_border = False

        if BUTTON_HOVER:
            button_hover = (HOVER_COLOR, HOVER_TEXT_COLOR)
        else:
            hover_color = False

        button_font = BUTTON_FONT_NAME, BUTTON_FONT_SIZE, BUTTON_FONT_COLOR, True, False

        restart_button_pos = (round(WIDTH / 2), self.scale_value(220))
        restart_button = Button('Restart', BUTTON_SIZE, restart_button_pos)

        main_menu_button_pos = (round(WIDTH / 2), self.scale_value(320))
        main_menu_button = Button('Menu', BUTTON_SIZE, main_menu_button_pos)

        run = True
        while run:

            surface.fill(BG_COLOR)
            clock.tick(FPS)

            # Displaying
            screen.blit(surface, (0, 0))
            screen.blit(header_render, header_text_rect.topleft)
            restart_button.blit(button_font, BUTTON_COLOR, button_border, button_hover)
            main_menu_button.blit(button_font, BUTTON_COLOR, button_border, button_hover)

            for event in pg.event.get():

                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
                    break

                if ((event.type == pg.KEYDOWN and event.key == pg.K_m) or
                        (event.type == pg.MOUSEBUTTONDOWN and event.button == 1 and main_menu_button.check_click())):
                    Button.remove_all_buttons()
                    CLICK_SOUND.play()

                    self.set_variables_to_default()
                    main()
                    run = False

                if ((event.type == pg.KEYDOWN and event.key == pg.K_RETURN) or
                        (event.type == pg.MOUSEBUTTONDOWN and event.button == 1 and restart_button.check_click())):

                    Button.remove_all_buttons()
                    CLICK_SOUND.play()

                    if self.game_mode == 'ai':
                        self.change_ai_player()

                    main(restart=True)
                    run = False

            pg.display.update()

    def set_game_data(self, data):

        with open(os.path.join(base_dir, DATA_FILE), 'wb') as f:
            pickle.dump(data, f)

    def set_variables_to_default(self):

        with open(os.path.join(base_dir, DATA_FILE), 'wb') as f:
            data = {'game mode': 'pvp', 'ai mode': None, 'ai player': None}
            pickle.dump(data, f)

    def change_ai_player(self):

        self.ai.ai_player = self.ai.get_other_player()

        with open(os.path.join(base_dir, DATA_FILE), 'wb') as f:
            data = {'game mode': self.game_mode, 'ai mode': self.ai.mode, 'ai player': self.ai.ai_player}
            pickle.dump(data, f)

    def draw_lines(self):

        for i in range(1, COLS):
            line_x = i * TILE_SIZE
            pg.draw.line(screen, LINE_COLOR, (line_x, 0), (line_x, HEIGHT), LINE_WIDTH)

        for j in range(1, ROWS):
            line_y = j * TILE_SIZE
            pg.draw.line(screen, LINE_COLOR, (0, line_y), (WIDTH, line_y), LINE_WIDTH)

    def draw_fig(self, row, col):

        center = self.center_of_tile(row, col)
        x, y = center

        if self.cur_player == 1:

            if SHARP_EDGE_CROSS:

                displacement = round((CROSS_LENGTH / mp.sqrt(2)) / 2)

                line1_start = (x - displacement, y - displacement)
                line1_end = (x + displacement, y + displacement)
                line2_start = (x - displacement, y + displacement)
                line2_end = (x + displacement, y - displacement)

                pg.draw.line(screen, CROSS_COLOR, line1_start, line1_end, CIRCLE_WIDTH)
                pg.draw.line(screen, CROSS_COLOR, line2_start, line2_end, CIRCLE_WIDTH)

            else:
                cross_size = (CROSS_WIDTH, CROSS_LENGTH)
                rect_surface = pg.Surface(cross_size)
                rect_surface.set_colorkey((0, 0, 0))
                rect_surface.fill(CROSS_COLOR)

                line1 = pg.transform.rotate(rect_surface, -45)
                line2 = pg.transform.rotate(rect_surface, 45)
                rotated_rect = line1.get_rect(center=center)

                screen.blit(line1, rotated_rect.topleft)
                screen.blit(line2, rotated_rect.topleft)

        elif self.cur_player == 2:
            pg.draw.circle(screen, CIRCLE_COLOR, center, CIRCLE_RADIUS, CIRCLE_WIDTH)

    def show_win(self, winner_player, orientation, first_element, last_element):

        WIN_SOUND.play()

        if winner_player == 1:
            color = CROSS_COLOR
        elif winner_player == 2:
            color = CIRCLE_COLOR

        if SHARP_EDGE_WIN:

            diagonal_offset = round(OFFSET / mp.sqrt(2))

            row_first, col_first = first_element
            row_last, col_last = last_element

            x_first_center, y_first_center = self.center_of_tile(row_first, col_first)
            x_last_center, y_last_center = self.center_of_tile(row_last, col_last)

            if orientation == 'horizontal':
                line_start = (x_first_center - OFFSET, y_first_center)
                line_end = (x_last_center + OFFSET, y_last_center)

            elif orientation == 'vertical':

                line_start = (x_first_center, y_first_center - OFFSET)
                line_end = (x_last_center, y_last_center + OFFSET)

            elif orientation == 'up diagonal':

                line_start = (x_first_center - diagonal_offset, y_first_center + diagonal_offset)
                line_end = (x_last_center + diagonal_offset, y_last_center - diagonal_offset)

            elif orientation == 'down diagonal':

                line_start = (x_first_center - diagonal_offset, y_first_center - diagonal_offset)
                line_end = (x_last_center + diagonal_offset, y_last_center + diagonal_offset)

            pg.draw.line(screen, color, line_start, line_end, WIN_WIDTH)

        if not SHARP_EDGE_WIN:

            row, col = first_element
            tile_x, tile_y = self.center_of_tile(row, col)

            if orientation in ['up diagonal', 'down diagonal']:

                length = ((ROWS - 1) * mp.sqrt(2) * TILE_SIZE) + (2 * OFFSET)
                center = (round(WIDTH / 2), round(HEIGHT / 2))

            else:
                length = (ROWS - 1) * TILE_SIZE + (2 * OFFSET)

            if orientation == 'horizontal':
                rotation = 90
                center = (round(WIDTH / 2), tile_y)

            elif orientation == 'vertical':
                rotation = 0
                center = (tile_x, round(HEIGHT / 2))

            elif orientation == 'up diagonal':
                rotation = -45

            elif orientation == 'down diagonal':
                rotation = 45

            line_surface = pg.Surface((WIN_WIDTH, length))
            line_surface.set_colorkey((0, 0, 0))
            line_surface.fill(color)

            line = pg.transform.rotate(line_surface, rotation)
            rotated_line = line.get_rect(center=center)
            screen.blit(line, rotated_line.topleft)

    def click_on_line(self, x, y):

        on_line = False

        for i in range(1, COLS):

            line_start = (i * TILE_SIZE) - (LINE_WIDTH // 2)
            line_end = (i * TILE_SIZE) + (LINE_WIDTH // 2)

            if line_start <= x <= line_end:
                on_line = True

        for j in range(1, ROWS):

            line_start = (j * TILE_SIZE) - (LINE_WIDTH // 2)
            line_end = (j * TILE_SIZE) + (LINE_WIDTH // 2)

            if line_start <= y <= line_end:
                on_line = True

        return on_line

    def center_of_tile(self, row, col):
        line_adjustment = LINE_WIDTH // 2

        left_x = TILE_SIZE * col
        right_x = TILE_SIZE * (col + 1)

        top_y = TILE_SIZE * row
        down_y = TILE_SIZE * (row + 1)

        if col == 0:
            right_x -= line_adjustment

        elif col == COLS - 1:
            left_x += line_adjustment

        else:
            left_x += line_adjustment
            right_x -= line_adjustment

        if row == 0:
            down_y -= line_adjustment

        elif row == ROWS - 1:
            top_y += line_adjustment

        else:
            top_y += line_adjustment
            down_y -= line_adjustment

        center_x = round((left_x + right_x) / 2)
        center_y = round((top_y + down_y) / 2)

        return (center_x, center_y)

    def scale_value(self, value, factor=FACTOR):

        return round(value * factor)


class Button:
    all_buttons = []

    def __init__(self, text, size, pos):

        self.text = text
        self.pos = pos
        self.button = pg.Rect(0, 0, size[0], size[1])
        self.button.center = self.pos
        self.hover = False
        self.pressed = False

        Button.add_button(self)

    @classmethod
    def add_button(cls, self):
        cls.all_buttons.append(self)

    @classmethod
    def remove_all_buttons(cls):
        pg.mouse.set_cursor(pg.cursors.Cursor(pg.SYSTEM_CURSOR_ARROW))
        cls.all_buttons = []

    @classmethod
    def change_cursor(cls):

        current_cursor = pg.mouse.get_cursor().data[0]

        if any([button.check_hover() for button in cls.all_buttons]):
            if current_cursor != pg.SYSTEM_CURSOR_HAND:
                pg.mouse.set_cursor(pg.cursors.Cursor(pg.SYSTEM_CURSOR_HAND))

        else:
            pg.mouse.set_cursor(pg.cursors.Cursor(pg.SYSTEM_CURSOR_ARROW))

    def check_hover(self):

        pos = pg.mouse.get_pos()
        if self.button.collidepoint(pos):
            return True

        return False

    def check_click(self):

        pos = pg.mouse.get_pos()
        if self.button.collidepoint(pos):
            return True

        return False

    def blit(self, font_info, box_color, border=None, hover=None):

        font_name, font_size, font_color, bold, italic = font_info

        hovering = self.check_hover()

        Button.change_cursor()

        if hover and hovering:
            color, font_color = hover

        else:
            color = box_color

        if border:
            border_width, border_color = border

            border_width_scale = 1 - border_width / self.button.width
            border_height_scale = 1 - border_width / self.button.height

            pg.draw.rect(screen, border_color, self.button, 0, BUTTON_RADIUS)
            self.border = self.button.scale_by(border_width_scale, border_height_scale)
            pg.draw.rect(screen, color, self.border, 0, BUTTON_RADIUS)

        else:
            pg.draw.rect(screen, color, self.button, 0, BUTTON_RADIUS)

        font = pg.font.SysFont(font_name, font_size, bold=bold, italic=italic)
        text_render = font.render(self.text, 1, font_color)
        text_rect = text_render.get_rect(center=self.pos)

        screen.blit(text_render, text_rect.topleft)

    def __repr__(self):
        return f'{self.text} Button'


def main(restart=False):
    game = Game()

    if not restart:
        game.start_screen()

    game.initialize_game()
    board = game.board

    if game.game_mode == 'ai':
        ai = game.ai

    while True and game.running:

        clock.tick(FPS)

        for event in pg.event.get():

            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
                break

            if event.type == pg.MOUSEBUTTONDOWN:

                x, y = event.pos

                if not game.click_on_line(x, y):

                    row = y // TILE_SIZE
                    col = x // TILE_SIZE

                    if board.check_empty(row, col) and game.running:
                        game.make_move(row, col)

                        if game.game_over():
                            game.running = False

        pg.display.update()

        if game.game_mode == 'ai' and game.cur_player == ai.ai_player and game.running:

            row, col = ai.ai_move()

            game.make_move(row, col)

            if game.game_over():
                game.running = False

            pg.display.update()

    pg.time.wait(2000)
    game.end_screen()

    if not restart:
        game.set_variables_to_default()


main()