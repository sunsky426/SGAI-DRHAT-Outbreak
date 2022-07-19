import enum

class Action(enum.Enum):
    move = 1
    bite = 2
    heal = 3
    kill = 4

class Direction(enum.Enum):
    up = 1
    down = 2
    left = 3
    right = 4