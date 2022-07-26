import enum
import pygame
import os
pygame.mixer.init()


ROWS = 6
COLUMNS = 6
BORDER = 150  # Number of pixels to offset grid to the top-left side
CELL_DIMENSIONS = (100, 100)  # Number of pixels (x,y) for each cell
SELF_PLAY = True  # whether or not a human will be playing
KILL_SOUND = pygame.mixer.Sound(os.path.join('Assets', 'Kill sound.mp3'))

class Action(enum.Enum):
    move = 1
    bite = 2
    heal = 3
    kill = 4

class Direction(enum.Enum):
    self = 0
    up = 1
    down = 2
    left = 3
    right = 4

class Role(enum.Enum):
    government = 0
    zombie = 1

reverse_dir = {
    Direction.up: Direction.down,
    Direction.down: Direction.up,
    Direction.left: Direction.right,
    Direction.right: Direction.left
}