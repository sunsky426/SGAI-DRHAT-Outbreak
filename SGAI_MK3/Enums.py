from audioop import reverse
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

class Role(enum.Enum):
    government = 0
    zombie = 1

reverse_dir = {
    Direction.up: Direction.down,
    Direction.down: Direction.up,
    Direction.left: Direction.right,
    Direction.right: Direction.left
}