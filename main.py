import pyxel
import random
import math
import enum
import time

import words
import constant

# import sounds
# ignore this for now
# canon = sounds.CanonD()


# Level class handles level
class Level(enum.Enum):
    LEVEL_ENDLESS = 0
    LEVEL_1 = 1
    LEVEL_2 = 2
    LEVEL_3 = 3
    LEVEL_WALLS = 4


    # Gamestate class handles gamestate (game over, screens)
class Gamestate(enum.Enum):
    GAME_OVER = 0
    MAIN_MENU = 1
    INSTRUCTIONS = 2
    LEVELS = 3
    CREDITS = 4
    RUNNING = 5
    WEREWOLVES_MOVING = 6
    PAUSED = 7
    WIN = 8
    ENDLESS_RUNNING = 9
    ENDLESS_GAME_OVER = 10
    WALLS_RUNNING = 11
    WALLS_GAME_OVER = 12


# lane class
class Lane(enum.Enum):
    LANE_0 = 0
    LANE_1 = 1
    LANE_2 = 2
    LANE_3 = 3
    LANE_4 = 4


def slay():
    print("Slay!")
    # canon.play()


def flash_image():
    pyxel.blt(5, 5, 1, 256, 256, 75, 96)


# helper function for calculation the start x value for centered text
def center_text_x(text, x, width, char_width=pyxel.FONT_WIDTH):
    text_width = len(text) * char_width
    return (width - text_width) / 2 + x


# helper function for calculation the start x value for centered text
def center_text_y(y, height, char_height=pyxel.FONT_HEIGHT):
    return (height - char_height) / 2 + y


# helper function to center any object
def center(width, page_width):
    return (page_width - width) / 2


# helper function to determine if two objects are overlapping
def is_overlapping(x1, y1, w1, h1, x2, y2, w2, h2):
    is_intersected = False
    if (x2 + w2 > x1 and x1 + w1 > x2 and y2 + h2 > y1 and y1 + h1 > y2):
        is_intersected = True
    return is_intersected


# Button class handles drawing and functionality of buttons
class Button:  # args contain the parameters for click_function
    def __init__(self,
                 x,
                 y,
                 w,
                 h,
                 col,
                 border_width,
                 border_col,
                 click_function,
                 parameters=(),
                 text="",
                 text_col=0):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.col = col
        self.border_width = border_width
        self.border_col = border_col
        self.click_function = click_function
        self.text = text
        self.text_col = text_col
        self.parameters = parameters
        self.is_hovering = False

    def on_click(self):
        print("Button pressed!")
        return self.click_function(*self.parameters)

    def set_hovering(self, hovering):
        if hovering and not self.is_hovering:
            self.is_hovering = True
            self.x = self.x - self.w * constant.HOVERING_EXPANSION_MULTIPLIER / 2
            self.y = self.y - self.h * constant.HOVERING_EXPANSION_MULTIPLIER / 2
            self.w += self.w * constant.HOVERING_EXPANSION_MULTIPLIER
            self.h += self.h * constant.HOVERING_EXPANSION_MULTIPLIER
        elif not hovering and self.is_hovering:
            self.is_hovering = False
            self.w = self.w / (1 + constant.HOVERING_EXPANSION_MULTIPLIER)
            self.h = self.h / (1 + constant.HOVERING_EXPANSION_MULTIPLIER)
            self.x = self.x + self.w * constant.HOVERING_EXPANSION_MULTIPLIER / 2
            self.y = self.y + self.h * constant.HOVERING_EXPANSION_MULTIPLIER / 2

    def draw(self):
        for i in range(self.border_width):
            i += 1
            pyxel.rectb(self.x - i, self.y - i, self.w + 2 * i, self.h + 2 * i,
                        self.border_col)
        pyxel.rect(self.x, self.y, self.w, self.h, self.col)
        pyxel.text(center_text_x(self.text, self.x, self.w),
                   center_text_y(self.y, self.h), self.text, self.text_col)


# PauseButton class is for the pause button (I didn't just want to create some random variables)
class PauseButton(Button):
    def __init__(self, *args, x, y, click_function):
        super().__init__(*args,
                         x=x,
                         y=y,
                         w=constant.PAUSE_BUTTON_WIDTH,
                         h=constant.PAUSE_BUTTON_HEIGHT,
                         col=constant.TRANSPARENT_COLOR,
                         border_width=0,
                         border_col=constant.TRANSPARENT_COLOR,
                         click_function=click_function,
                         text="",
                         text_col=constant.TRANSPARENT_COLOR)
        self.is_paused = False
        self.is_endless = False
        self.is_walls = False
        self.walls = False

    def set_hovering(self, hovering):
        pass

    def on_click(self):
        if self.is_paused:
            if self.is_walls:
                self.click_function(Gamestate.WALLS_RUNNING)
            if self.is_endless:
                self.click_function(Gamestate.ENDLESS_RUNNING)
            else:
                self.click_function(Gamestate.RUNNING)
            self.is_paused = False
        else:
            self.click_function(Gamestate.PAUSED)
            self.is_paused = True

    def draw(self):
        if self.is_paused:
            pyxel.blt(self.x, self.y, constant.IMAGE_BANK_NUMBER,
                      constant.PLAY_BUTTON_U, constant.PLAY_BUTTON_V, self.w,
                      self.h, constant.TRANSPARENT_COLOR)
        else:
            pyxel.blt(self.x, self.y, constant.IMAGE_BANK_NUMBER,
                      constant.PAUSE_BUTTON_U, constant.PAUSE_BUTTON_V, self.w,
                      self.h, constant.TRANSPARENT_COLOR)


# Menu class handles containing and drawing menus (such as the pause menu, the game over menu, etc) (does not draw text)
class Menu:
    def __init__(self,
                 x,
                 y,
                 w,
                 h,
                 col,
                 border_width=0,
                 border_col=0,
                 **kwargs):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.col = col
        self.border_width = border_width
        self.border_col = border_col
        self.buttons = kwargs["buttons"]  # has to be a dictionary

    def update(self):
        for button_key in self.buttons:
            button = self.buttons[button_key]
            if is_overlapping(button.x, button.y, button.w, button.h,
                              pyxel.mouse_x, pyxel.mouse_y, 1, 1):
                button.set_hovering(True)
                if pyxel.btn(pyxel.MOUSE_BUTTON_LEFT):
                    button.set_hovering(False)
                elif pyxel.btnr(pyxel.MOUSE_BUTTON_LEFT):
                    button.on_click()
            else:
                button.set_hovering(False)

    def draw(self):
        pyxel.rect(self.x, self.y, self.w, self.h, self.col)
        for i in range(self.border_width):
            i += 1
            pyxel.rectb(self.x - i, self.y - i, self.w + 2 * i, self.h + 2 * i,
                        self.border_col)
        for button_key in self.buttons:
            button = self.buttons[button_key]
            button.draw()


# werewolf class prints and moves werewolves
class Werewolf:
    def __init__(self, x, y, x_vel=2):
        self.x = x
        self.y = y
        self.w = constant.CELL_WIDTH
        self.h = constant.CELL_HEIGHT
        self.new_x = x
        self.x_vel = x_vel

    def move(self, new_x):
        self.new_x = new_x
        if self.x > self.new_x:
            self.x -= self.x_vel

    def draw(self):
        pyxel.blt(self.x, self.y, 1, constant.WEREWOLF_U, constant.WEREWOLF_V,
                  constant.CELL_WIDTH, constant.CELL_HEIGHT,
                  constant.WEREWOLF_TRANSPARENT_COLOR)

    def dead_animation(self):
        pass  # idk if we'll use this


# Armored_Werewolf class draws armored werewolves
class Armored_Werewolf(Werewolf):
    def draw(self):
        pyxel.blt(self.x, self.y, 1, constant.ARMORED_WEREWOLF_U,
                  constant.ARMORED_WEREWOLF_V, constant.CELL_WIDTH,
                  constant.CELL_HEIGHT, constant.WEREWOLF_TRANSPARENT_COLOR)


class Bullet:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.w = constant.BULLET_WIDTH
        self.h = constant.BULLET_HEIGHT
        self.vel_x = constant.BULLET_SPEED

    def is_overlapping(self, u, v, w, h):
        return is_overlapping(self.x, self.y, self.w, self.h, u, v, w, h)

    def move(self):
        self.x += self.vel_x

    def draw(self):
        pyxel.blt(self.x, self.y, constant.IMAGE_BANK_NUMBER,
                  constant.BULLET_U, constant.BULLET_V, self.w, self.h,
                  constant.TRANSPARENT_COLOR)


# guess class handles user input for guesses and such I guess...
class Guess:
    def __init__(self):
        self.word_to_guess = words.FIVE_LETTER_WORDS_LIST[random.randrange(
            len(words.FIVE_LETTER_WORDS_LIST))].upper()
        self.guess_letter = ""
        self.correct_guesses = []
        self.wrong_guesses = []
        self.valid_letters = "ABCDEFGHIJKLMNOPQRSTTUVWXYZ"

    def enter_guess(self):  # haha I made this like 50 lines less
        try:
            if pyxel.input_keys[0]:  # if there is input
                letter = chr(pyxel.input_keys[0]).upper()
                if letter not in self.correct_guesses and letter not in self.wrong_guesses and letter in self.valid_letters:  # make sure the input is a letter of the alphabet and also not guessed already
                    self.guess_letter = letter
        except:
            pass
        if pyxel.btnp(pyxel.KEY_BACKSPACE):
            self.guess_letter = ""

    def check_guess(self):  # returns if the letter being guessed is in the word, and the bullets to fire
        bullets_to_fire = 0
        if self.guess_letter:  # if there is a letter being guessed
            if self.guess_letter not in self.correct_guesses and self.guess_letter not in self.wrong_guesses:  # if the letter has not been guessed already
                if self.guess_letter in self.word_to_guess:  # if the letter is correct
                    self.correct_guesses.append(
                        self.guess_letter)  # add it to the correct guesses
                    for letter in self.word_to_guess:
                        if letter == self.guess_letter:
                            bullets_to_fire += 1
                    self.guess_letter = ""  # reset the saved letter
                    return (True, bullets_to_fire)

                else:
                    self.wrong_guesses.append(self.guess_letter)
                    self.guess_letter = ""  # reset the saved letter
                    return (False, 0)
            self.guess_letter = ""  # reset the saved letter
        return (True, 0)  # we need to return something for the other cases

    def draw(self):
        # draw wrong guesses
        pyxel.text(10, 10, "Wrong Letters:", 0)
        i = 0
        for letter in self.wrong_guesses:
            pyxel.text(10 + 5 * (i % constant.LETTERS_PER_ROW),
                       20 + 6 * math.floor(i / constant.LETTERS_PER_ROW),
                       letter, 0)
            i += 1

        # draw current guess
        pyxel.text(100, 238, "Current Guess: " + self.guess_letter, 0)

        # draw word
        temp_word = ""  # temp_word stores the output
        for letter in self.word_to_guess:
            if letter in self.correct_guesses:
                temp_word += letter
            else:
                temp_word += "_"  # using underscores to show which words we don't have right now
        pyxel.text(80, 10, temp_word, 0)


# to edit the resources.pyxres, type pyxel edit assets/resources.pyxres into the shell
class App:
    def __init__(self):
        pyxel.init(384,
                   256,
                   title="Words vs Werewolves",
                   fps=30,
                   quit_key=pyxel.KEY_ESCAPE,
                   display_scale=2)
        pyxel.load("assets/resources.pyxres")  # load the assets
        pyxel.mouse(True)  # make the mouse visible for now

        pyxel.image(1).load(256, 256, "assets/ivy.png")
        pyxel.image(1).load(constant.WEREWOLF_U, constant.WEREWOLF_V,
                            "assets/wgray3.png")
        pyxel.image(1).load(constant.ARMORED_WEREWOLF_U,
                            constant.ARMORED_WEREWOLF_V, "assets/wgold3.png")

        # time
        self.time_last_frame = time.time()
        self.dt = 0
        self.time_since_move = 0
        self.time_alive = 0

        self.level = Level.LEVEL_1
        self.gamestate = Gamestate.MAIN_MENU

        self.werewolf_vel = 0.4

        # pause button
        self.pause_button = PauseButton(x=350,
                                        y=7,
                                        click_function=self.change_gamestate)

        # here are the menus (a class that handles multiple buttons and stuff)
        self.main_menu = Menu(x=0,
                              y=0,
                              w=0,
                              h=0,
                              col=0,
                              border_width=0,
                              border_col=0,
                              buttons={
                                  "start game":
                                  Button(x=center(60, pyxel.width),
                                         y=40,
                                         w=60,
                                         h=24,
                                         col=9,
                                         border_width=2,
                                         border_col=4,
                                         click_function=self.change_gamestate,
                                         parameters=[Gamestate.LEVELS],
                                         text="Play",
                                         text_col=7),
                                  "endless":
                                  Button(x=center(60, pyxel.width),
                                         y=68,
                                         w=60,
                                         h=10,
                                         col=4,
                                         border_width=2,
                                         border_col=9,
                                         click_function=self.start_endless,
                                         text="Endless Mode",
                                         text_col=7),
                                  "walls":
                                  Button(x=center(60, pyxel.width),
                                         y=79,
                                         w=60,
                                         h=10,
                                         col=4,
                                         border_width=2,
                                         border_col=9,
                                         click_function=self.start_walls,
                                         text="Wall Mode",
                                         text_col=7),
                                  "instructions":
                                  Button(x=center(60, pyxel.width),
                                         y=94,
                                         w=60,
                                         h=12,
                                         col=9,
                                         border_width=2,
                                         border_col=7,
                                         click_function=self.change_gamestate,
                                         parameters=[Gamestate.INSTRUCTIONS],
                                         text="How to Play",
                                         text_col=7),
                                  "levels":
                                  Button(x=center(60, pyxel.width) + 70,
                                         y=94,
                                         w=40,
                                         h=12,
                                         col=9,
                                         border_width=2,
                                         border_col=7,
                                         click_function=self.change_gamestate,
                                         parameters=[Gamestate.LEVELS],
                                         text="Levels",
                                         text_col=7),
                                  "credits":
                                  Button(x=center(60, pyxel.width) - 50,
                                         y=94,
                                         w=40,
                                         h=12,
                                         col=9,
                                         border_width=2,
                                         border_col=7,
                                         click_function=self.change_gamestate,
                                         parameters=[Gamestate.CREDITS],
                                         text="Credits",
                                         text_col=7),
                                  "slay":
                                  Button(x=8,
                                         y=7,
                                         w=25,
                                         h=15,
                                         col=3,
                                         border_width=0,
                                         border_col=0,
                                         click_function=slay,
                                         text="Slay!",
                                         text_col=0)
                              })

        self.levels_menu = Menu(
            x=center(constant.LEVELS_MENU_WIDTH, pyxel.width),
            y=33,
            w=constant.LEVELS_MENU_WIDTH,
            h=constant.LEVELS_MENU_HEIGHT,
            col=0,
            border_width=0,
            border_col=7,
            buttons={
                "level1":
                Button(x=center(80, pyxel.width),
                       y=20,
                       w=80,
                       h=15,
                       col=7,
                       border_width=1,
                       border_col=13,
                       click_function=self.go_to_level,
                       parameters=[Level.LEVEL_1],
                       text="Level One",
                       text_col=12),
                "level2":
                Button(x=center(80, pyxel.width),
                       y=45,
                       w=80,
                       h=15,
                       col=7,
                       border_width=1,
                       border_col=13,
                       click_function=self.go_to_level,
                       parameters=[Level.LEVEL_2],
                       text="Level Two",
                       text_col=5),
                "level3":
                Button(x=center(80, pyxel.width),
                       y=70,
                       w=80,
                       h=15,
                       col=7,
                       border_width=1,
                       border_col=13,
                       click_function=self.go_to_level,
                       parameters=[Level.LEVEL_3],
                       text="Level Three",
                       text_col=1),
                "menu":
                Button(x=center(80, pyxel.width),
                       y=105,
                       w=80,
                       h=15,
                       col=13,
                       border_width=1,
                       border_col=7,
                       click_function=self.return_to_main_menu,
                       text="Back to Main Menu",
                       text_col=7)
            })

        self.credits_menu = Menu(
            x=center(constant.CREDITS_MENU_WIDTH, pyxel.width),
            y=33,
            w=constant.CREDITS_MENU_WIDTH,
            h=constant.CREDITS_MENU_HEIGHT,
            col=0,
            border_width=1,
            border_col=7,
            buttons={
                "menu":
                Button(x=center(80, pyxel.width),
                       y=80,
                       w=80,
                       h=15,
                       col=0,
                       border_width=1,
                       border_col=7,
                       click_function=self.return_to_main_menu,
                       text="Back to Main Menu",
                       text_col=7)
            })

        self.instructions_menu = Menu(
            x=center(constant.INSTRUCTIONS_MENU_WIDTH, pyxel.width),
            y=33,
            w=constant.INSTRUCTIONS_MENU_WIDTH,
            h=constant.INSTRUCTIONS_MENU_HEIGHT,
            col=0,
            border_width=1,
            border_col=7,
            buttons={  #sorry its this y
                "menu":
                Button(x=center(80, pyxel.width),
                       y=80,
                       w=80,
                       h=15,
                       col=0,
                       border_width=1,
                       border_col=7,
                       click_function=self.return_to_main_menu,
                       text="Back to Main Menu",
                       text_col=7)
            })  # change the y to move the box upwards (lower y is higher)

        self.game_over_menu = Menu(
            x=center(constant.GAME_OVER_MENU_WIDTH, pyxel.width),
            y=33,
            w=constant.GAME_OVER_MENU_WIDTH,
            h=constant.GAME_OVER_MENU_HEIGHT,
            col=0,
            border_width=1,
            border_col=7,
            buttons={
                "restart":
                Button(x=center(60, pyxel.width),
                       y=61,
                       w=60,
                       h=15,
                       col=0,
                       border_width=1,
                       border_col=7,
                       click_function=self.restart,
                       text="Restart",
                       text_col=7),
                "menu":
                Button(x=center(60, pyxel.width),
                       y=80,
                       w=60,
                       h=15,
                       col=0,
                       border_width=1,
                       border_col=7,
                       click_function=self.return_to_main_menu,
                       text="Main Menu",
                       text_col=7)
            })

        self.endless_game_over_menu = Menu(
            x=center(constant.GAME_OVER_MENU_WIDTH, pyxel.width),
            y=33,
            w=constant.GAME_OVER_MENU_WIDTH,
            h=constant.GAME_OVER_MENU_HEIGHT,
            col=0,
            border_width=1,
            border_col=7,
            buttons={
                "restart":
                Button(x=center(60, pyxel.width),
                       y=61,
                       w=60,
                       h=15,
                       col=0,
                       border_width=1,
                       border_col=7,
                       click_function=self.start_endless,
                       text="Restart",
                       text_col=7),
                "menu":
                Button(x=center(60, pyxel.width),
                       y=80,
                       w=60,
                       h=15,
                       col=0,
                       border_width=1,
                       border_col=7,
                       click_function=self.return_to_main_menu,
                       text="Main Menu",
                       text_col=7)
            })

        self.walls_game_over_menu = Menu(
            x=center(constant.GAME_OVER_MENU_WIDTH, pyxel.width),
            y=33,
            w=constant.GAME_OVER_MENU_WIDTH,
            h=constant.GAME_OVER_MENU_HEIGHT,
            col=0,
            border_width=1,
            border_col=7,
            buttons={
                "restart":
                Button(x=center(60, pyxel.width),
                       y=61,
                       w=60,
                       h=15,
                       col=0,
                       border_width=1,
                       border_col=7,
                       click_function=self.start_walls,
                       text="Restart",
                       text_col=7),
                "menu":
                Button(x=center(60, pyxel.width),
                       y=80,
                       w=60,
                       h=15,
                       col=0,
                       border_width=1,
                       border_col=7,
                       click_function=self.return_to_main_menu,
                       text="Main Menu",
                       text_col=7)
            })

        self.win_menu = Menu(x=center(constant.WIN_MENU_WIDTH, pyxel.width),
                             y=33,
                             w=constant.WIN_MENU_WIDTH,
                             h=constant.WIN_MENU_HEIGHT,
                             col=0,
                             border_width=1,
                             border_col=7,
                             buttons={
                                 "next_level":
                                 Button(x=center(60, pyxel.width),
                                        y=61,
                                        w=60,
                                        h=15,
                                        col=0,
                                        border_width=1,
                                        border_col=7,
                                        click_function=self.next_level,
                                        text="Next Level",
                                        text_col=7),
                                 "menu":
                                 Button(
                                     x=center(60, pyxel.width),
                                     y=80,
                                     w=60,
                                     h=15,
                                     col=0,
                                     border_width=1,
                                     border_col=7,
                                     click_function=self.return_to_main_menu,
                                     text="Main Menu",
                                     text_col=7)
                             })

        self.pause_menu = Menu(
            x=center(constant.PAUSE_MENU_WIDTH, pyxel.width),
            y=33,
            w=constant.PAUSE_MENU_WIDTH,
            h=constant.PAUSE_MENU_HEIGHT,
            col=0,
            border_width=1,
            border_col=7,
            buttons={
                "unpause":
                Button(x=center(60, pyxel.width),
                       y=61,
                       w=60,
                       h=15,
                       col=0,
                       border_width=1,
                       border_col=7,
                       click_function=self.pause_button.on_click,
                       text="Resume",
                       text_col=7),
                "menu":
                Button(x=center(60, pyxel.width),
                       y=80,
                       w=60,
                       h=15,
                       col=0,
                       border_width=1,
                       border_col=7,
                       click_function=self.return_to_main_menu,
                       text="Main Menu",
                       text_col=7)
            })

        # werewolves
        self.werewolves = {
            Level.LEVEL_1: [
                Werewolf(constant.GRID_X + 7 * constant.CELL_WIDTH,
                         constant.GRID_Y + 2 * constant.CELL_HEIGHT),
                Werewolf(constant.GRID_X + 8 * constant.CELL_WIDTH,
                         constant.GRID_Y + 1 * constant.CELL_HEIGHT),
                Werewolf(constant.GRID_X + 8 * constant.CELL_WIDTH,
                         constant.GRID_Y + 3 * constant.CELL_HEIGHT),
                Werewolf(constant.GRID_X + 9 * constant.CELL_WIDTH,
                         constant.GRID_Y + 0 * constant.CELL_HEIGHT),
                Werewolf(constant.GRID_X + 9 * constant.CELL_WIDTH,
                         constant.GRID_Y + 4 * constant.CELL_HEIGHT)
            ],
            Level.LEVEL_2: [],
            Level.LEVEL_3: [],
            Level.LEVEL_ENDLESS: [
                Werewolf(constant.GRID_X + 10 * constant.CELL_WIDTH,
                         constant.GRID_Y + 2 * constant.CELL_HEIGHT,
                         self.werewolf_vel),
                Werewolf(constant.GRID_X + 11 * constant.CELL_WIDTH,
                         constant.GRID_Y + 1 * constant.CELL_HEIGHT,
                         self.werewolf_vel),
                Werewolf(constant.GRID_X + 11 * constant.CELL_WIDTH,
                         constant.GRID_Y + 3 * constant.CELL_HEIGHT,
                         self.werewolf_vel),
                Werewolf(constant.GRID_X + 12 * constant.CELL_WIDTH,
                         constant.GRID_Y + 0 * constant.CELL_HEIGHT,
                         self.werewolf_vel),
                Werewolf(constant.GRID_X + 12 * constant.CELL_WIDTH,
                         constant.GRID_Y + 4 * constant.CELL_HEIGHT,
                         self.werewolf_vel)
            ],
            Level.LEVEL_WALLS: [
                Werewolf(constant.GRID_X + 10 * constant.CELL_WIDTH,
                         constant.GRID_Y + 2 * constant.CELL_HEIGHT,
                         self.werewolf_vel),
                Werewolf(constant.GRID_X + 11 * constant.CELL_WIDTH,
                         constant.GRID_Y + 1 * constant.CELL_HEIGHT,
                         self.werewolf_vel),
                Werewolf(constant.GRID_X + 11 * constant.CELL_WIDTH,
                         constant.GRID_Y + 3 * constant.CELL_HEIGHT,
                         self.werewolf_vel),
                Werewolf(constant.GRID_X + 12 * constant.CELL_WIDTH,
                         constant.GRID_Y + 0 * constant.CELL_HEIGHT,
                         self.werewolf_vel),
                Werewolf(constant.GRID_X + 12 * constant.CELL_WIDTH,
                         constant.GRID_Y + 4 * constant.CELL_HEIGHT,
                         self.werewolf_vel)
            ]
        }

        # bullets
        self.bullets = []

        # grid
        self.grid_w = 8
        self.grid_h = 5

        self.werewolves_killed = 0
        self.time_to_spawn_werewolf = 5 + 5 * random.random()
        self.letters_right = 0
        self.chance_of_armored_werewolf = 0.2
        self.min_time_to_spawn_werewolf = 5
        self.time_range_to_spawn_werewolf = 5
        self.wave_summoned = True
        self.bullets_to_fire = 0

        self.word = Guess()  # move this later

        self.score = 0

        print(self.word.word_to_guess)

        pyxel.run(self.update, self.draw)

    def reset(self, gamestate=Gamestate.MAIN_MENU, level=Level.LEVEL_1):
        self.level = level
        self.gamestate = gamestate
        self.time_last_frame = time.time()
        self.dt = 0
        self.time_since_move = 0
        self.time_alive = 0
        self.grid_w = 8
        self.grid_h = 5
        self.word = Guess()  # move this later
        print(self.word.word_to_guess)
        self.score = 0
        self.pause_button.is_paused = False
        self.werewolves_killed = 0
        self.time_to_spawn_werewolf = 5 + 5 * random.random()
        self.letters_right = 0
        self.chance_of_armored_werewolf = 0.2
        self.min_time_to_spawn_werewolf = 5
        self.time_range_to_spawn_werewolf = 5
        self.werewolf_vel = 0.4
        self.wave_summoned = True
        self.pause_button.is_endless = False
        self.pause_button.is_walls = False
        self.bullets_to_fire = 0

        # put wolves here
        self.werewolves = {
            Level.LEVEL_1: [
                Werewolf(constant.GRID_X + 7 * constant.CELL_WIDTH,
                         constant.GRID_Y + 2 * constant.CELL_HEIGHT),
                Werewolf(constant.GRID_X + 8 * constant.CELL_WIDTH,
                         constant.GRID_Y + 1 * constant.CELL_HEIGHT),
                Werewolf(constant.GRID_X + 8 * constant.CELL_WIDTH,
                         constant.GRID_Y + 3 * constant.CELL_HEIGHT),
                Werewolf(constant.GRID_X + 9 * constant.CELL_WIDTH,
                         constant.GRID_Y + 0 * constant.CELL_HEIGHT),
                Werewolf(constant.GRID_X + 9 * constant.CELL_WIDTH,
                         constant.GRID_Y + 4 * constant.CELL_HEIGHT)
            ],
            Level.LEVEL_2: [
                Werewolf(constant.GRID_X + 5 * constant.CELL_WIDTH,
                         constant.GRID_Y + 0 * constant.CELL_HEIGHT),
                Werewolf(constant.GRID_X + 6 * constant.CELL_WIDTH,
                         constant.GRID_Y + 1 * constant.CELL_HEIGHT),
                Werewolf(constant.GRID_X + 7 * constant.CELL_WIDTH,
                         constant.GRID_Y + 2 * constant.CELL_HEIGHT),
                Werewolf(constant.GRID_X + 8 * constant.CELL_WIDTH,
                         constant.GRID_Y + 3 * constant.CELL_HEIGHT),
                Werewolf(constant.GRID_X + 9 * constant.CELL_WIDTH,
                         constant.GRID_Y + 4 * constant.CELL_HEIGHT)
            ],
            Level.LEVEL_3: [
                Werewolf(constant.GRID_X + 7 * constant.CELL_WIDTH,
                         constant.GRID_Y + 2 * constant.CELL_HEIGHT),
                Werewolf(constant.GRID_X + 8 * constant.CELL_WIDTH,
                         constant.GRID_Y + 1 * constant.CELL_HEIGHT),
                Werewolf(constant.GRID_X + 8 * constant.CELL_WIDTH,
                         constant.GRID_Y + 3 * constant.CELL_HEIGHT),
                Werewolf(constant.GRID_X + 9 * constant.CELL_WIDTH,
                         constant.GRID_Y + 0 * constant.CELL_HEIGHT),
                Werewolf(constant.GRID_X + 9 * constant.CELL_WIDTH,
                         constant.GRID_Y + 4 * constant.CELL_HEIGHT)
            ],
            Level.LEVEL_ENDLESS: [
                Werewolf(constant.GRID_X + 10 * constant.CELL_WIDTH,
                         constant.GRID_Y + 2 * constant.CELL_HEIGHT,
                         self.werewolf_vel),
                Werewolf(constant.GRID_X + 11 * constant.CELL_WIDTH,
                         constant.GRID_Y + 1 * constant.CELL_HEIGHT,
                         self.werewolf_vel),
                Werewolf(constant.GRID_X + 11 * constant.CELL_WIDTH,
                         constant.GRID_Y + 3 * constant.CELL_HEIGHT,
                         self.werewolf_vel),
                Werewolf(constant.GRID_X + 12 * constant.CELL_WIDTH,
                         constant.GRID_Y + 0 * constant.CELL_HEIGHT,
                         self.werewolf_vel),
                Werewolf(constant.GRID_X + 12 * constant.CELL_WIDTH,
                         constant.GRID_Y + 4 * constant.CELL_HEIGHT,
                         self.werewolf_vel)
            ],
            Level.LEVEL_WALLS: [
                Werewolf(constant.GRID_X + 7 * constant.CELL_WIDTH,
                         constant.GRID_Y + 2 * constant.CELL_HEIGHT),
                Werewolf(constant.GRID_X + 8 * constant.CELL_WIDTH,
                         constant.GRID_Y + 1 * constant.CELL_HEIGHT),
                Werewolf(constant.GRID_X + 8 * constant.CELL_WIDTH,
                         constant.GRID_Y + 3 * constant.CELL_HEIGHT),
                Werewolf(constant.GRID_X + 9 * constant.CELL_WIDTH,
                         constant.GRID_Y + 0 * constant.CELL_HEIGHT),
                Werewolf(constant.GRID_X + 9 * constant.CELL_WIDTH,
                         constant.GRID_Y + 4 * constant.CELL_HEIGHT)
            ]
        }

        self.bullets = []

    def restart(self):
        self.reset(Gamestate.RUNNING)

    def restart_endless(self):
        self.reset(Gamestate.ENDLESS_RUNNING)

    def restart_walls(self):
        self.reset(Gamestate.WALLS_RUNNING)

    def return_to_main_menu(self):
        self.reset(Gamestate.MAIN_MENU)

    def next_level(self):
        self.reset(gamestate=Gamestate.RUNNING,
                   level=Level(self.level.value + 1))

    def change_gamestate(self, gamestate):
        self.gamestate = gamestate

    def start_endless(self):
        self.reset(Gamestate.ENDLESS_RUNNING, Level.LEVEL_ENDLESS)
        self.pause_button.is_endless = True
        self.move_werewolves(2 * pyxel.width)

    def start_walls(self):
        self.reset(Gamestate.WALLS_RUNNING, Level.LEVEL_WALLS)
        self.pause_button.is_walls = True

    def go_to_level(self, level):
        self.reset(Gamestate.RUNNING, level)

    def move_werewolves(self, move_distance=0):
        for werewolf in self.werewolves[self.level]:
            werewolf.move(werewolf.new_x - move_distance)

    def create_werewolf(self, werewolf_array, x, lane, new_x=0, x_vel=2):
        werewolf_array.append(
            Werewolf(x, constant.GRID_Y + lane * constant.CELL_HEIGHT, x_vel))
        werewolf_array[-1].move(new_x)

    def create_armored_werewolf(self,
                                werewolf_array,
                                x,
                                lane,
                                new_x=0,
                                x_vel=2):
        werewolf_array.append(
            Armored_Werewolf(x, constant.GRID_Y + lane * constant.CELL_HEIGHT,
                             x_vel))
        werewolf_array[-1].move(new_x)
        self.create_werewolf(werewolf_array=werewolf_array,
                             x=x,
                             lane=lane,
                             new_x=new_x,
                             x_vel=x_vel)

    def create_wave_of_werewolves(self,
                                  werewolf_array,
                                  x,
                                  new_x=0,
                                  x_vel=2,
                                  chance_of_armored_werewolf=0):
        for lane in range(5):
            if random.random() <= chance_of_armored_werewolf:
                self.create_armored_werewolf(werewolf_array=werewolf_array,
                                             x=x,
                                             lane=lane,
                                             new_x=new_x,
                                             x_vel=x_vel)
            else:
                self.create_werewolf(werewolf_array=werewolf_array,
                                     x=x,
                                     lane=lane,
                                     new_x=new_x,
                                     x_vel=x_vel)

    def werewolves_speed_up(self, multiplier):
        for werewolf in self.werewolves[self.level]:
            werewolf.x_vel *= multiplier

    def update(self):
        # canon.update()

        if pyxel.btnp(pyxel.KEY_ESCAPE):
            pyxel.quit()

        # just for finding coordinates
        if pyxel.btnp(pyxel.KEY_TAB):
            print((pyxel.mouse_x, pyxel.mouse_y))

        if self.gamestate == Gamestate.MAIN_MENU:
            self.main_menu.update()

        elif self.gamestate == Gamestate.RUNNING:
            # if there are no werewolves
            if len(self.werewolves[self.level]) == 0:
                self.gamestate = Gamestate.WIN
                return  # to stop the if statement here
            if self.werewolves[self.level][0].x < constant.GRID_X:
                self.gamestate = Gamestate.GAME_OVER
            self.word.enter_guess()

            if is_overlapping(self.pause_button.x, self.pause_button.y,
                              self.pause_button.w, self.pause_button.h,
                              pyxel.mouse_x, pyxel.mouse_y, 1, 1):
                if pyxel.btnr(pyxel.MOUSE_BUTTON_LEFT):
                    self.pause_button.on_click()

            if self.level == Level.LEVEL_3:  # to add more levels with timer, just add them as an or statement here and created another if (with the time till move)
                time_this_frame = time.time()
                self.dt = time_this_frame - self.time_last_frame
                self.time_last_frame = time_this_frame
                self.time_since_move += self.dt

            if (self.time_since_move >= 5) and (self.level == Level.LEVEL_3):
                #print(self.word.word_to_guess)
                self.gamestate = Gamestate.WEREWOLVES_MOVING
                self.move_werewolves(constant.CELL_WIDTH)
                self.time_last_frame = time.time()
                self.dt = 0
                self.time_since_move = 0

            if pyxel.btnp(pyxel.KEY_RETURN) or pyxel.btnp(pyxel.KEY_SPACE):
                guess_correct, bullets_to_fire = self.word.check_guess()
                if not guess_correct:
                    self.gamestate = Gamestate.WEREWOLVES_MOVING
                    self.move_werewolves(constant.CELL_WIDTH)
                    # reset time thingies
                    self.time_last_frame = time.time()
                    self.dt = 0
                    self.time_since_move = 0
                    self.score += 1
                else:
                    for bullet_index in range(bullets_to_fire):
                        self.bullets.append(
                            Bullet(
                                10, self.werewolves[self.level][len(
                                    self.bullets)].y + 3))

            # move the bullets
            for bullet in self.bullets:
                bullet.move()

            # check if bullet hit a werewolf
            for bullet_index in range(len(self.bullets)):
                wolf = self.werewolves[self.level][bullet_index]
                if self.bullets[bullet_index].is_overlapping(
                        wolf.x, wolf.y, wolf.w, wolf.h):
                    # remove the bullet and werewolf from the array
                    self.bullets.pop(bullet_index)
                    self.werewolves[self.level].pop(bullet_index)
                    break

        elif self.gamestate == Gamestate.ENDLESS_RUNNING:
            try:
                if self.werewolves[self.level][
                        0].x < constant.GRID_X - constant.CELL_WIDTH:
                    self.gamestate = Gamestate.ENDLESS_GAME_OVER
                    return
            except:
                pass
            self.word.enter_guess()

            if pyxel.btnp(pyxel.KEY_DELETE):  # for debugging
                self.time_alive += (60 - self.time_alive % 60)
                self.wave_summoned = False

            if self.time_since_move >= self.time_to_spawn_werewolf:  # summon werewolf
                self.time_to_spawn_werewolf = self.min_time_to_spawn_werewolf + self.time_range_to_spawn_werewolf * random.random(
                )  # time to summon next werewolf
                self.time_since_move = 0
                # change the range between werewolf spawns:
                self.min_time_to_spawn_werewolf = 5 - self.time_alive / 60 / 3 * 2  # decrease it by 2 every 3 minutes
                if self.min_time_to_spawn_werewolf <= 2:
                    self.min_time_to_spawn_werewolf = 2  # the minimum is this number

                self.time_range_to_spawn_werewolf = 5 - self.time_alive / 60  # decrease it by 1 every 1 minute
                if self.time_range_to_spawn_werewolf <= 1:
                    self.time_range_to_spawn_werewolf = 1

                if random.random() <= self.chance_of_armored_werewolf:
                    self.create_armored_werewolf(
                        werewolf_array=self.werewolves[self.level],
                        x=constant.GRID_X + 10 * constant.CELL_WIDTH,
                        lane=random.randrange(5),
                        x_vel=self.werewolf_vel)
                else:
                    self.create_werewolf(
                        werewolf_array=self.werewolves[self.level],
                        x=constant.GRID_X + 10 * constant.CELL_WIDTH,
                        lane=random.randrange(5),
                        x_vel=self.werewolf_vel)

                for bullet_index in range(self.bullets_to_fire):
                    try:
                        self.bullets.append(
                            Bullet(
                                10, self.werewolves[self.level][len(
                                    self.bullets)].y + 3))
                        self.bullets_to_fire -= 1
                    except:
                        pass

            if is_overlapping(self.pause_button.x, self.pause_button.y,
                              self.pause_button.w, self.pause_button.h,
                              pyxel.mouse_x, pyxel.mouse_y, 1, 1):
                if pyxel.btnr(pyxel.MOUSE_BUTTON_LEFT):
                    self.pause_button.on_click()

            if pyxel.btnp(pyxel.KEY_RETURN) or pyxel.btnp(pyxel.KEY_SPACE):
                guess_correct, bullets_to_fire = self.word.check_guess()
                if not guess_correct:
                    self.werewolves_speed_up(
                        1 + constant.ENDLESS_WRONG_GUESS_MULTIPLIER)

                else:
                    self.bullets_to_fire += bullets_to_fire
                    for bullet_index in range(self.bullets_to_fire):
                        try:
                            self.bullets.append(
                                Bullet(
                                    10, self.werewolves[self.level][len(
                                        self.bullets)].y + 3))
                            self.bullets_to_fire -= 1
                        except:
                            pass
                    self.letters_right += bullets_to_fire
                    if self.letters_right == 5:
                        self.word = Guess()
                        self.letters_right = 0

            # every minute summon a wave of werewolves
            if self.time_alive % 60 < 1 and not self.wave_summoned:
                self.wave_summoned = True
                # number of waves increases every 10 minutes
                number_of_waves = math.floor(
                    (self.time_alive / 60 - 1) / 10) + 1
                # every 2 minutes increased the chance by 1/5, reseting to 0/5 at 11 minutes and 21 minutes, etc.
                print(number_of_waves)
                chance_of_armored_werewolf = (
                    math.floor(self.time_alive / 60 / 2) - 5 *
                    (number_of_waves - 1)) / 5
                print(chance_of_armored_werewolf)
                for wave in range(
                        number_of_waves):  # create waves of werewolves
                    self.create_wave_of_werewolves(
                        werewolf_array=self.werewolves[self.level],
                        x=constant.GRID_X + (10 + wave) * constant.CELL_WIDTH,
                        x_vel=self.werewolf_vel,
                        chance_of_armored_werewolf=chance_of_armored_werewolf)

                self.time_since_move = -15  # give player 15 seconds of no summoning
                if self.chance_of_armored_werewolf < 0.5:  # if the chance is less than 0.5, increase it by 0.03 every minute
                    self.chance_of_armored_werewolf += 0.03

            if self.time_alive % 60 > 30 and self.wave_summoned:
                self.wave_summoned = False

            self.move_werewolves()

            # move the bullets
            for bullet in self.bullets:
                bullet.move()

            # check if bullet hit a werewolf
            for bullet_index in range(len(self.bullets)):
                wolf = self.werewolves[self.level][bullet_index]
                if self.bullets[bullet_index].is_overlapping(
                        wolf.x, wolf.y, wolf.w, wolf.h):
                    # remove the bullet and werewolf from the array
                    self.bullets.pop(bullet_index)
                    self.werewolves[self.level].pop(bullet_index)
                    self.werewolves_killed += 1
                    break

            time_this_frame = time.time()
            self.dt = time_this_frame - self.time_last_frame
            self.time_since_move += self.dt
            self.time_alive += self.dt
            self.time_last_frame = time_this_frame

        elif self.gamestate == Gamestate.ENDLESS_GAME_OVER:
            self.endless_game_over_menu.update()

        # move the wolves (if they need to be moved)
        elif self.gamestate == Gamestate.WEREWOLVES_MOVING:
            self.move_werewolves()
            # time so gamestate stays as WEREWOLVES_MOVING for WEREWOLF_MOVING_TIME
            time_this_frame = time.time()
            self.dt = time_this_frame - self.time_last_frame
            self.time_last_frame = time_this_frame
            self.time_since_move += self.dt
            if self.time_since_move >= constant.WEREWOLF_MOVING_TIME:
                self.gamestate = Gamestate.RUNNING
            # pause button functionality
            if is_overlapping(self.pause_button.x, self.pause_button.y,
                              self.pause_button.w, self.pause_button.h,
                              pyxel.mouse_x, pyxel.mouse_y, 1, 1):
                if pyxel.btnr(pyxel.MOUSE_BUTTON_LEFT):
                    self.pause_button.on_click()

            # move the bullets
            for bullet in self.bullets:
                bullet.move()

            # check if bullet hit a werewolf
            for bullet_index in range(len(self.bullets)):
                wolf = self.werewolves[self.level][bullet_index]
                if self.bullets[bullet_index].is_overlapping(
                        wolf.x, wolf.y, wolf.w, wolf.h):
                    # remove the bullet and werewolf from the array
                    self.bullets.pop(bullet_index)
                    self.werewolves[self.level].pop(bullet_index)
                    break

        elif self.gamestate == Gamestate.WALLS_RUNNING:
            try:
                if self.werewolves[self.level][
                        0].x < constant.GRID_X - constant.CELL_WIDTH:
                    self.gamestate = Gamestate.WALLS_GAME_OVER
                    return

            except:
                pass

            self.word.enter_guess()
            if pyxel.btnp(pyxel.KEY_RETURN) or pyxel.btnp(pyxel.KEY_SPACE):
                guess_correct, bullets_to_fire = self.word.check_guess()
                if not guess_correct:
                    self.gamestate = Gamestate.WEREWOLVES_MOVING
                    self.move_werewolves(constant.CELL_WIDTH)
                    # reset time thingies
                    self.time_last_frame = time.time()
                    self.dt = 0
                    self.time_since_move = 0
                    self.score += 1

                if guess_correct:
                    pass
            if self.time_since_move >= self.time_to_spawn_werewolf:  # summon werewolf
                self.time_to_spawn_werewolf = self.min_time_to_spawn_werewolf + self.time_range_to_spawn_werewolf * random.random(
                )  # time to summon next werewolf
                self.time_since_move = 0
                # change the range between werewolf spawns:
                self.min_time_to_spawn_werewolf = 5 - self.time_alive / 60 / 3 * 2  # decrease it by 2 every 3 minutes
                if self.min_time_to_spawn_werewolf <= 2:
                    self.min_time_to_spawn_werewolf = 2  # the minimum is this number

                self.time_range_to_spawn_werewolf = 5 - self.time_alive / 60  # decrease it by 1 every 1 minute
                if self.time_range_to_spawn_werewolf <= 1:
                    self.time_range_to_spawn_werewolf = 1

                if random.random() <= self.chance_of_armored_werewolf:
                    self.create_armored_werewolf(
                        werewolf_array=self.werewolves[self.level],
                        x=constant.GRID_X + 10 * constant.CELL_WIDTH,
                        lane=random.randrange(5),
                        x_vel=self.werewolf_vel)
                else:
                    self.create_werewolf(
                        werewolf_array=self.werewolves[self.level],
                        x=constant.GRID_X + 10 * constant.CELL_WIDTH,
                        lane=random.randrange(5),
                        x_vel=self.werewolf_vel)

        elif self.gamestate == Gamestate.PAUSED:
            self.dt = 0
            self.time_last_frame = time.time()
            self.pause_menu.update()
            if pyxel.btnr(pyxel.MOUSE_BUTTON_LEFT):
                if is_overlapping(self.pause_button.x, self.pause_button.y,
                                  self.pause_button.w, self.pause_button.h,
                                  pyxel.mouse_x, pyxel.mouse_y, 1, 1):
                    self.pause_button.on_click()

        elif self.gamestate == Gamestate.GAME_OVER:
            self.game_over_menu.update()

        elif self.gamestate == Gamestate.WIN:
            self.win_menu.update()

        elif self.gamestate == Gamestate.INSTRUCTIONS:
            self.instructions_menu.update()

        elif self.gamestate == Gamestate.LEVELS:
            self.levels_menu.update()

        elif self.gamestate == Gamestate.CREDITS:
            self.credits_menu.update()

    def draw_grid(self):  # temporary
        for x in range(self.grid_w):
            for y in range(self.grid_h):
                pyxel.rectb(constant.GRID_X + x * constant.CELL_WIDTH,
                            constant.GRID_Y + y * constant.CELL_HEIGHT,
                            constant.CELL_WIDTH, constant.CELL_HEIGHT, 11)
        pyxel.rectb(constant.GRID_X - 1, constant.GRID_Y, 2,
                    constant.CELL_HEIGHT * 5, 8)
        pyxel.image(2).load(constant.BACKGROUND_U, constant.BACKGROUND_V, "assets/quad 1.png")
        pyxel.blt(207, 0, 2, constant.BACKGROUND_U, constant.BACKGROUND_V, constant.BACKGROUND_U + 384, constant.BACKGROUND_V + 192, 0)
        pyxel.image(2).load(constant.BACKGROUND_U, constant.BACKGROUND_V, "assets/quad 2.png")
        pyxel.blt(207, 128, 2, constant.BACKGROUND_U, constant.BACKGROUND_V, constant.BACKGROUND_U + 384, constant.BACKGROUND_V + 192, 0)
        pyxel.image(2).load(constant.BACKGROUND_U, constant.BACKGROUND_V, "assets/quad 3.png")
        pyxel.blt(0, 128, 2, constant.BACKGROUND_U, constant.BACKGROUND_V, constant.BACKGROUND_U + 384, constant.BACKGROUND_V + 192, 0)
        pyxel.image(2).load(constant.BACKGROUND_U, constant.BACKGROUND_V, "assets/quad 4.png")
        pyxel.blt(0, 0, 2, constant.BACKGROUND_U, constant.BACKGROUND_V, constant.BACKGROUND_U + 384, constant.BACKGROUND_V + 192, 0)
        pyxel.blt(0, 128, 0, 0, 110, 8*4, 8 * 5, 0) #house

    def draw(self):
        pyxel.cls(0)
        if self.gamestate == Gamestate.MAIN_MENU:
            pyxel.text(center_text_x("Words vs Werewolves", 0, pyxel.width),
                       16, "Words vs Werewolves",
                       math.floor(pyxel.frame_count / 15) % 16)
            self.main_menu.draw()

        elif self.gamestate == Gamestate.INSTRUCTIONS:
            self.instructions_menu.draw()
            pyxel.text(
                center_text_x("This game is similar to Hangman!", 0,
                              pyxel.width), 40,
                "This game is similar to hangman.", 7)
            pyxel.text(
                center_text_x("Simply type the letter you think is in", 0,
                              pyxel.width), 52,
                "Simply type the letter you think is in", 7)
            pyxel.text(
                center_text_x("the word and hit 'Enter' or the space bar'", 0,
                              pyxel.width), 64,
                "the word and hit 'Enter' or the space bar", 7)

        elif self.gamestate == Gamestate.LEVELS:
            self.levels_menu.draw()
            #self.lvl1_button = (x = 172, y = 7, click_function = self.change_gamestate)
            #if level 1 button pressed
            #self.gamestate == Gamestate.RUNNING
            #self.level = LEVEL_1
        #if level 2 button pressed
        #self.gamestate == Gamestate.RUNNING
        #self.level = LEVEL_2
        #if level 3 button pressed
        #self.gamestate == Gamestate.RUNNING
        #self.level = LEVEL_3

        elif self.gamestate == Gamestate.CREDITS:
            self.credits_menu.draw()
            pyxel.text(center_text_x("Created by:", 0, pyxel.width), 40,
                       "Created by:", 7)
            # pyxel.rectb(center_text_x("Made by:", 0, pyxel.width), 40 + pyxel.FONT_HEIGHT, len("Made by:") * pyxel.FONT_WIDTH, 1, 7) # make an underline!
            pyxel.text(center_text_x("Sophie DePaul", 0, pyxel.width), 48,
                       "Sophie DePaul", 7)
            pyxel.text(center_text_x("Lucia Lacourtna", 0, pyxel.width), 54,
                       "Lucia Lacourtna", 7)
            pyxel.text(center_text_x("Cory \"Kyra\" Zhou", 0, pyxel.width), 60,
                       "Cory \"Kyra\" Zhou", 7)

        elif self.gamestate == Gamestate.RUNNING or self.gamestate == Gamestate.PAUSED or self.gamestate == Gamestate.WEREWOLVES_MOVING or self.gamestate == Gamestate.GAME_OVER or self.gamestate == Gamestate.WIN or self.gamestate == Gamestate.ENDLESS_RUNNING or self.gamestate == Gamestate.ENDLESS_GAME_OVER or self.gamestate == Gamestate.WALLS_RUNNING or self.gamestate == Gamestate.WALLS_GAME_OVER:
            if self.gamestate != Gamestate.ENDLESS_RUNNING and self.gamestate != Gamestate.ENDLESS_GAME_OVER and self.level != Level.LEVEL_ENDLESS:
                pyxel.text(136, 10, "Score: " + str(self.score), 7)
            else:
                pyxel.text(109, 6, "Time: " + str(round(self.time_alive, 2)),
                           7)
                pyxel.text(109, 14,
                           "Kill Count: " + str(self.werewolves_killed), 7)
                pyxel.text(109, 22, "Bullets: " + str(self.bullets_to_fire), 7)

            # draw grid
            self.draw_grid()

            # draw werewolves:
            for wolf in reversed(
                    self.werewolves[self.level]
            ):  # reversed to draw armored ones after normal (when they overlap)
                wolf.draw()

            # draw bullets
            for bullet in self.bullets:
                bullet.draw()

            self.word.draw()
            self.pause_button.draw()

        if self.gamestate == Gamestate.WEREWOLVES_MOVING:
            pass

        if self.gamestate == Gamestate.PAUSED:
            self.pause_menu.draw()
            pyxel.text(center_text_x("The game is paused", 0, pyxel.width), 42,
                       "The game is paused", 7)
            if random.randrange(500) == 1:  # easter egg hehe
                flash_image()

        if self.gamestate == Gamestate.GAME_OVER:
            self.game_over_menu.draw()
            pyxel.text(center_text_x("Game Over", 0, pyxel.width), 40,
                       "Game Over", 7)
            pyxel.text(center_text_x("The word was: _____", 0, pyxel.width),
                       50, "The word was: " + self.word.word_to_guess, 7)

        if self.gamestate == Gamestate.WIN:
            self.win_menu.draw()
            pyxel.text(center_text_x("Congratulations!", 0, pyxel.width), 40,
                       "Congratulations", 7)
            pyxel.text(center_text_x("The word was: _____", 0, pyxel.width),
                       50, "The word was: " + self.word.word_to_guess, 7)

        if self.gamestate == Gamestate.ENDLESS_RUNNING:
            pass

        if self.gamestate == Gamestate.ENDLESS_GAME_OVER:
            self.endless_game_over_menu.draw()
            pyxel.text(center_text_x("Game Over", 0, pyxel.width), 40,
                       "Game Over", 7)
            pyxel.text(center_text_x("The word was: _____", 0, pyxel.width),
                       50, "The word was: " + self.word.word_to_guess, 7)


App()
