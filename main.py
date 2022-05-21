import pyxel

import time
import random
import enum

import collections
import numpy

from shortest_path_alg_BFS import shortestPath


# enum inspo: https://docs.python.org/3.11/howto/enum.html
# define direction
class Direction(enum.Enum):
    RIGHT = 0
    DOWN = 1
    LEFT = 2
    UP = 3


# game state control
class GameControl(enum.Enum):
    RUNNING = 0
    GAME_OVER = 1


# game mode control
class GameMode(enum.Enum):
    NOBODY_PLAYS = 0
    PLAYER_PLAYS = 1
    AI_PLAYS = 2


# drawing game space
class Level:
    def __init__(self):
        self.tm = 0
        self.u = 0
        self.v = 0
        self.w = 16
        self.h = 16

    def draw(self):
        pyxel.bltm(0, 0, self.tm, self.u, self.v, self.w, self.h)


# drawing and moving of an egg
class Egg:
    def __init__(self, x, y):
        self.x = x  # x coord.
        self.y = y  # y coord.
        self.w = 8  # width
        self.h = 8  # height

    def draw(self):
        pyxel.blt(self.x, self.y, 0, 16, 0, self.w, self.h)

    def collisions(self, u, v, w, h):
        is_collided = False
        if (
                u + w > self.x
                and
                self.x + self.w > u
                and
                v + h > self.y
                and
                self.y + self.h > v
        ):
            is_collided = True
            return is_collided

    def move(self, moved_x, moved_y):
        self.x = moved_x
        self.y = moved_y


# drawing and moving snake
class SnakePart:
    def __init__(self, x, y, is_head=False, is_tail=False):

        self.x = x  # x coord.
        self.y = y  # y coord.
        self.w = 8  # width
        self.h = 8  # height
        self.is_head = is_head
        self.is_tail = is_tail

    def draw(self, direction):
        width = self.w
        height = self.h
        texture_x = 0
        texture_y = 0

        # flippin head
        if self.is_head:
            if direction == direction.RIGHT:
                texture_x = 8
                texture_y = 0
            if direction == direction.LEFT:
                texture_x = 8
                texture_y = 0
                width = width * -1
            if direction == direction.DOWN:
                texture_x = 0
                texture_y = 8
            if direction == direction.UP:
                texture_x = 0
                texture_y = 8
                height = height * -1

        if self.is_tail:
            if direction == direction.RIGHT:
                texture_x = 8
                texture_y = 8
            if direction == direction.LEFT:
                texture_x = 8
                texture_y = 8
                width = width * -1
            if direction == direction.DOWN:
                texture_x = 16
                texture_y = 8
            if direction == direction.UP:
                texture_x = 16
                texture_y = 8
                height = height * -1

        pyxel.blt(self.x, self.y, 0, texture_x, texture_y, width, height)

    def collisions(self, u, v, w, h):
        is_collided = False
        if (
                u + w > self.x
                and
                self.x + self.w > u
                and
                v + h > self.y
                and
                self.y + self.h > v
        ):
            is_collided = True
            return is_collided


# alignment fcns
def align_center(text, page_width, char_width=pyxel.FONT_WIDTH):
    text_width = len(text) * char_width
    return (page_width - text_width) / 2


def align_middle(screen_height, char_height=pyxel.FONT_HEIGHT):
    return (screen_height - char_height) / 2


def align_right(text, screen_width, char_width=pyxel.FONT_WIDTH):
    text_width = len(text) * char_width
    return screen_width - (text_width + char_width)


# drawing fcns for logos, scores, etc...
class Display:
    def __init__(self):
        self.game_start_menu = "Welcome to Snake Game"
        self.game_start_menu_choice_1 = "Press 1 to Play Game"
        self.game_start_menu_choice_2 = "Press 2 to watch AI"
        self.game_start_menu_x = align_center(self.game_start_menu, 128)
        self.game_start_menu_choice_1_x = align_center(self.game_start_menu_choice_1, 128)
        self.game_start_menu_choice_2_x = align_center(self.game_start_menu_choice_2, 128)
        self.game_start_menu_y = align_middle(128) - 2 * 8
        self.game_over = "GAME OVER."
        self.game_over_prompt = "Press the 'Enter' key to start."
        self.game_over_x = align_center(self.game_over, 128)
        self.game_over_y = align_middle(128)
        self.game_over_prompt_x = align_center(self.game_over_prompt, 128)
        self.title = "SNAKE"
        self.title_x = align_center(self.title, 128)
        self.score = str(0)
        self.score_x = align_right(self.score, 128)
        self.egg_count = "Eggs "
        self.egg_count_x = 9

    def draw_title(self):
        pyxel.rect(self.title_x - 1, 0, len(self.title) * pyxel.FONT_WIDTH + 1, pyxel.FONT_HEIGHT + 1, 1)
        pyxel.text(self.title_x, 1, self.title, 12)

    def draw_score(self, score):
        self.score = str(score)
        self.score_x = align_right(self.score, 128)
        pyxel.rect(self.score_x - 1, 0, len(self.score) * pyxel.FONT_WIDTH + 1, pyxel.FONT_HEIGHT + 1, 1)
        pyxel.text(self.score_x, 1, self.score, 3)

    def draw_eggs(self, eggs):
        self.egg_count = "Eggs " + str(eggs)
        pyxel.rect(self.egg_count_x - 1, 0, len(self.egg_count) * pyxel.FONT_WIDTH + 1, pyxel.FONT_HEIGHT + 1, 1)
        pyxel.text(self.egg_count_x, 1, self.egg_count, 8)

    def draw_game_over(self):
        pyxel.rect(self.game_over_prompt_x - 4, self.game_over_y - 4,
                   len(self.game_over_prompt) * pyxel.FONT_WIDTH + 10, 2 * pyxel.FONT_HEIGHT + 10, 1)
        pyxel.text(self.game_over_x, self.game_over_y, self.game_over, 8)
        pyxel.text(self.game_over_prompt_x, self.game_over_y + pyxel.FONT_HEIGHT + 2, self.game_over_prompt, 8)

    def draw_start_menu(self):
        pyxel.rect(8, 8,
                   112, 112, 1)
        pyxel.text(self.game_start_menu_x, self.game_start_menu_y, self.game_start_menu, 8)
        pyxel.text(self.game_start_menu_choice_1_x, self.game_start_menu_y + pyxel.FONT_HEIGHT + 2,
                   self.game_start_menu_choice_1, 8)
        pyxel.text(self.game_start_menu_choice_2_x, self.game_start_menu_y + 2 * pyxel.FONT_HEIGHT + 4,
                   self.game_start_menu_choice_2, 8)


class App:
    def __init__(self):
        self.manh_dist_x = int()
        self.manh_dist_y = int()
        self.snake_len = int()
        self.matrix_list = []
        self.origin_x = 32 / 8
        self.origin_y = 32 / 8
        self.shortest_path = collections.deque()
        self.first_move = numpy.empty((1, 2))
        self.matrix = numpy.zeros((16, 16), dtype=int)
        self.x_move = 0
        self.y_move = 0
        pyxel.init(128, 128, scale=8, caption="Snake", fps=120)
        pyxel.load("assets/resources.pyxres")
        self.current_game_state = GameControl.GAME_OVER
        self.current_game_mode = GameMode.NOBODY_PLAYS
        self.level = Level()
        self.Display = Display()
        self.moved_x = 64
        self.moved_y = 32
        self.Egg = Egg(64, 32)
        self.snake = []  # store snake sections
        self.snake.append(SnakePart(32, 32, is_head=True))
        self.snake.append(SnakePart(24, 32))
        self.snake.append(SnakePart(16, 32))
        self.snake.append(SnakePart(8, 32, is_tail=True))
        self.snake_direction: Direction = Direction.RIGHT
        self.sections_to_add = 0
        self.speed = 1
        self.time_last_frame = time.time()
        self.dt = 0
        self.time_since_last_move = 0
        self.input_queue = collections.deque()  # store directions
        self.eggs_collected = 0
        self.score = 0
        pyxel.run(self.update, self.draw)

    def start_new_game(self):
        self.current_game_state = GameControl.RUNNING
        self.snake.clear()
        self.snake.append(SnakePart(32, 32, is_head=True))
        self.snake.append(SnakePart(24, 32))
        self.snake.append(SnakePart(16, 32))
        self.snake.append(SnakePart(8, 32, is_tail=True))
        self.snake_direction: Direction = Direction.RIGHT
        self.sections_to_add = 0
        self.speed = 1
        self.time_last_frame = time.time()
        self.dt = 0
        self.time_since_last_move = 0
        self.input_queue.clear()
        self.move_Egg()
        self.eggs_collected = 0
        self.score = 0

    def update(self):
        time_this_frame = time.time()
        self.dt = time_this_frame - self.time_last_frame
        self.time_last_frame = time_this_frame
        self.time_since_last_move += self.dt
        if self.current_game_mode == GameMode.NOBODY_PLAYS:
            self.check_input_gamemode()
        if self.current_game_mode == GameMode.PLAYER_PLAYS:
            self.check_input()
        # elif self.current_game_mode == GameMode.AI_PLAYS:
        if self.current_game_state == GameControl.RUNNING:
            if self.current_game_mode == GameMode.PLAYER_PLAYS:
                if self.time_since_last_move >= 1 / self.speed:
                    self.time_since_last_move = 0
                    self.move_snake()
                    self.check_collisions()
            elif self.current_game_mode == GameMode.AI_PLAYS:
                if self.time_since_last_move >= 1 / self.speed:
                    self.snake_AI()
                    self.check_AI_input()
                    self.move_snake()
                    self.time_since_last_move = 0
                    self.check_collisions()

    # draw snake, scores, egg...
    def draw(self):
        pyxel.cls(0)
        self.level.draw()
        self.Egg.draw()

        for i in self.snake:
            i.draw(self.snake_direction)
        self.Display.draw_title()
        self.Display.draw_score(self.score)
        self.Display.draw_eggs(self.eggs_collected)
        if self.current_game_state == GameControl.GAME_OVER:
            self.Display.draw_start_menu()

    def check_collisions(self):
        # Egg
        if self.Egg.collisions(self.snake[0].x, self.snake[0].y, self.snake[0].w, self.snake[0].h):
            self.speed += (self.speed * 0.1)
            self.sections_to_add += 1
            self.move_Egg()
            self.eggs_collected += 1
            self.score += len(self.snake) * self.eggs_collected + 1
        # snake
        for i in self.snake:
            if i == self.snake[0]:
                continue
            if i.collisions(self.snake[0].x, self.snake[0].y, self.snake[0].w, self.snake[0].h):
                time.sleep(3)
                self.current_game_state = GameControl.GAME_OVER
                self.current_game_mode = GameMode.NOBODY_PLAYS
        # borders
        if pyxel.tilemap(0).get(self.snake[0].x / 8, self.snake[0].y / 8) == 3:
            time.sleep(3)
            self.current_game_state = GameControl.GAME_OVER
            self.current_game_mode = GameMode.NOBODY_PLAYS

    def move_Egg(self):
        # new location
        good_position = False
        while not good_position:
            moved_x = random.randrange(8, 120, 8)
            moved_y = random.randrange(8, 120, 8)
            good_position = True

            # collision check
            for i in self.snake:
                if (
                        moved_x + 8 > i.x
                        and
                        i.x + i.w > moved_x
                        and
                        moved_y + 8 > i.y
                        and
                        i.y + i.h > moved_y
                ):
                    good_position = False
                    break
                if good_position:
                    self.Egg.move(moved_x, moved_y)

                    self.moved_x = moved_x
                    self.moved_y = moved_y

    def move_snake(self):
        # change direction
        # global s
        if len(self.input_queue):
            self.snake_direction = self.input_queue.popleft()
        # grow snake
        if self.sections_to_add > 0:
            self.snake.insert(2, SnakePart(self.snake[1].x, self.snake[1].y))
            self.sections_to_add -= 1
        # move head
        prev_location_x = self.snake[0].x
        prev_location_y = self.snake[0].y
        if self.snake_direction == Direction.RIGHT:
            self.snake[0].x += self.snake[0].w
        if self.snake_direction == Direction.LEFT:
            self.snake[0].x -= self.snake[0].w
        if self.snake_direction == Direction.DOWN:
            self.snake[0].y += self.snake[0].w
        if self.snake_direction == Direction.UP:
            self.snake[0].y -= self.snake[0].w
        # move rest of the snake
        for i in self.snake:
            if i == self.snake[0]:
                continue
            curr_location_x = i.x
            curr_location_y = i.y
            i.x = prev_location_x
            i.y = prev_location_y
            prev_location_x = curr_location_x
            prev_location_y = curr_location_y

    # check input in menu
    def check_input_gamemode(self):
        if self.current_game_state == GameControl.GAME_OVER:
            if pyxel.btn(pyxel.KEY_1):
                self.start_new_game()
                self.current_game_mode = GameMode.PLAYER_PLAYS

            elif pyxel.btn(pyxel.KEY_2):
                self.start_new_game()
                self.current_game_mode = GameMode.AI_PLAYS

    # check key input
    def check_input(self):

        if pyxel.btn(pyxel.KEY_RIGHT):
            if len(self.input_queue) == 0:
                if self.snake_direction != Direction.LEFT and self.snake_direction != Direction.RIGHT:
                    self.input_queue.append(Direction.RIGHT)
            else:
                if self.input_queue[-1] != Direction.LEFT and self.input_queue[-1] != Direction.RIGHT:
                    self.input_queue.append(Direction.RIGHT)

        elif pyxel.btn(pyxel.KEY_LEFT):
            if len(self.input_queue) == 0:
                if self.snake_direction != Direction.RIGHT and self.snake_direction != Direction.LEFT:
                    self.input_queue.append(Direction.LEFT)
            else:
                if self.input_queue[-1] != Direction.RIGHT and self.input_queue[-1] != Direction.LEFT:
                    self.input_queue.append(Direction.LEFT)

        elif pyxel.btn(pyxel.KEY_DOWN):
            if len(self.input_queue) == 0:
                if self.snake_direction != Direction.UP and self.snake_direction != Direction.DOWN:
                    self.input_queue.append(Direction.DOWN)
            else:
                if self.input_queue[-1] != Direction.UP and self.input_queue[-1] != Direction.DOWN:
                    self.input_queue.append(Direction.DOWN)

        elif pyxel.btn(pyxel.KEY_UP):
            if len(self.input_queue) == 0:
                if self.snake_direction != Direction.DOWN and self.snake_direction != Direction.UP:
                    self.input_queue.append(Direction.UP)
            else:
                if self.input_queue[-1] != Direction.DOWN and self.input_queue[-1] != Direction.UP:
                    self.input_queue.append(Direction.UP)

    def snake_AI(self):

        self.manh_dist_x = (self.snake[0].x - self.moved_x) / 8
        self.manh_dist_y = (self.snake[0].y - self.moved_y) / 8
        self.snake_len = len(self.snake)

        self.origin_x = self.snake[0].x // 8
        self.origin_y = self.snake[0].y // 8

        # matrix start
        self.matrix = numpy.zeros((16, 16), dtype=int)
        self.matrix[0, :] = 1
        self.matrix[-1, :] = 1
        self.matrix[:, -1] = 1
        self.matrix[:, 0] = 1

        # Egg to matrix
        self.matrix[self.moved_y // 8, self.moved_x // 8] = 0

        # snake to matrix
        for i in self.snake:
            self.matrix[i.y // 8, i.x // 8] = 1

        self.matrix[self.origin_y, self.origin_x] = 0

        self.matrix_list = self.matrix.tolist()

        # compute shortest path by calling a dedicated fcn
        self.shortest_path = shortestPath(self.matrix_list, self.origin_y, self.origin_x, self.moved_y // 8,
                                          self.moved_x // 8)

        # compute direction based on ShortestPath fcn output
        if len(self.shortest_path) == 1:
            # just admit your loss by making a wrong move intentionally :D
            self.x_move, self.y_move = 2, 2
        else:
            while self.shortest_path[1] != ():
                #
                self.first_move = numpy.asarray(self.shortest_path[1])
                snake_head = numpy.asarray([self.origin_y, self.origin_x])
                result_move = self.first_move - snake_head
                self.x_move, self.y_move = result_move[0], result_move[1]
                break

    # define direction based on output of SnakeAi fcn
    def check_AI_input(self):

        if self.x_move == 0 and self.y_move == 1:
            if len(self.input_queue) == 0:
                if self.snake_direction != Direction.LEFT and self.snake_direction != Direction.RIGHT:
                    self.input_queue.append(Direction.RIGHT)
            else:
                if self.input_queue[-1] != Direction.LEFT and self.input_queue[-1] != Direction.RIGHT:
                    self.input_queue.append(Direction.RIGHT)

        elif self.x_move == 0 and self.y_move == -1:
            if len(self.input_queue) == 0:
                if self.snake_direction != Direction.RIGHT and self.snake_direction != Direction.LEFT:
                    self.input_queue.append(Direction.LEFT)
            else:
                if self.input_queue[-1] != Direction.RIGHT and self.input_queue[-1] != Direction.LEFT:
                    self.input_queue.append(Direction.LEFT)

        elif self.x_move == 1 and self.y_move == 0:
            if len(self.input_queue) == 0:
                if self.snake_direction != Direction.UP and self.snake_direction != Direction.DOWN:
                    self.input_queue.append(Direction.DOWN)
            else:
                if self.input_queue[-1] != Direction.UP and self.input_queue[-1] != Direction.DOWN:
                    self.input_queue.append(Direction.DOWN)

        elif self.x_move == -1 and self.y_move == 0:
            if len(self.input_queue) == 0:
                if self.snake_direction != Direction.DOWN and self.snake_direction != Direction.UP:
                    self.input_queue.append(Direction.UP)
            else:
                if self.input_queue[-1] != Direction.DOWN and self.input_queue[-1] != Direction.UP:
                    self.input_queue.append(Direction.UP)

        # when there is no move left
        else:
            self.input_queue.append(Direction.UP)


App()
