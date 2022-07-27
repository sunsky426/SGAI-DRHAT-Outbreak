from typing import Tuple
import pygame
from constants import *
from Board import Board


# constants
BACKGROUND = "#DDC2A1"
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
CELL_COLOR = (233, 222, 188)
SAFE_COLOR = (93, 138, 168)
LINE_WIDTH = 5
GAME_WINDOW_DIMENSIONS = (1200, 800)
RESET_MOVE_COORDS = (800, 600)
RESET_MOVE_DIMS = (200, 50)

# Initialize pygame
screen = pygame.display.set_mode(GAME_WINDOW_DIMENSIONS)
pygame.display.set_caption("Outbreak!")
pygame.font.init()
font = pygame.font.SysFont("Impact", 30)
pygame.display.set_caption("Outbreak!")
screen.fill(BACKGROUND)


def get_action(GameBoard: Board, pixel_x: int, pixel_y: int):
    """
    Get the action that the click represents.
    If the click was on the heal or kill button, returns Action.heal or Action.kill respectively
    Else, returns the board coordinates of the click (board_x, board_y) if valid
    Return None otherwise
    """
    # Check if the user clicked on the "heal" icon, return "heal" if so

    heal_bite_check = pixel_x >= 900 and pixel_x <= 1100 and pixel_y > 190 and pixel_y < 301
    kill_check = pixel_x >= 800 and pixel_x <= 900 and pixel_y > 199 and pixel_y < 301
    Med_check = pixel_x >= 800 and pixel_x <= 900 and pixel_y > 301 and pixel_y < 401
    reset_move_check = (
        pixel_x >= RESET_MOVE_COORDS[0]
        and pixel_x <= RESET_MOVE_COORDS[0] + RESET_MOVE_DIMS[0]
        and pixel_y >= RESET_MOVE_COORDS[1]
        and pixel_y <= RESET_MOVE_COORDS[1] + RESET_MOVE_DIMS[1]
    )
    board_x = int((pixel_x - 150) / 100)
    board_y = int((pixel_y - 150) / 100)
    move_check = (
        board_x >= 0
        and board_x < GameBoard.columns
        and board_y >= 0
        and board_y < GameBoard.rows
    )
    board_coords = (int((pixel_x - 150) / 100), int((pixel_y - 150) / 100))

    if heal_bite_check:
        if GameBoard.player_role == Role.government:
            return Action.heal
        else:
            return Action.bite
    elif Med_check:
        return "Distrb Med"
    elif kill_check:
        return Action.kill
    elif reset_move_check:
        return "reset move"
    elif move_check:
        return board_coords
    return None


def run(GameBoard: Board):
    """
    Draw the screen and return any events.
    """
    screen.fill(BACKGROUND)
    build_grid(GameBoard)  # Draw the grid
    
    # Draw the heal icon
    if GameBoard.player_role == Role.government:
        display_image(screen, "Assets/cure.jpeg", GameBoard.display_cell_dimensions, (950, 200))
        display_image(screen, "Assets/kill.png", GameBoard.display_cell_dimensions, (800, 200))
        display_image(screen, "Assets/RedCross.png", GameBoard.display_cell_dimensions, (800, 300))
    else:
        display_image(screen, "Assets/bite.png", GameBoard.display_cell_dimensions, (950, 200))
    #Draw the kill button slightly to the left of heal
    display_people(GameBoard)
    display_reset_move_button()
    
    return pygame.event.get()


def disp_title_screen():
    """
    Displays a basic title screen with title, start button, and quit button
    """
    start_text = font.render('START', True, WHITE)
    quit_text = font.render('QUIT', True, WHITE)
    screen.fill(BACKGROUND)
    #Draw title
    display_image(screen, "Assets/Outbreak_title.png", (1048, 238), (76, 100))
    #Check if the user has clicked either start or quit
    while True:
        mouse = pygame.mouse.get_pos()
        #Draw the start and quit buttons (They might need a little bit more work at some point, they're not centered well)
        pygame.draw.rect(screen,BLACK,[500,350,200,100])
        pygame.draw.rect(screen,BLACK,[500,500,200,100])
        screen.blit(start_text, (560, 375))
        screen.blit(quit_text, (570, 525))
        for i in pygame.event.get():
            if i.type == pygame.MOUSEBUTTONDOWN:
                if 500 <= mouse[0] <= 700 and 350 <= mouse[1] <= 450:
                    return True
                elif 500 <= mouse[0] <= 700 and 500 <= mouse[1] <= 600:
                        pygame.display.quit()
                        break
        pygame.display.update()

def display_safe_space(GameBoard):
    """
    Creates a blue rectangle at every safe space state
    """
    for state in GameBoard.States:
        if state.safeSpace:
            coords = (
                int(GameBoard.toCoord(state.location)[0]) * GameBoard.display_cell_dimensions[0]
                + GameBoard.display_border,
                int(GameBoard.toCoord(state.location)[1]) * GameBoard.display_cell_dimensions[1]
                + GameBoard.display_border,
            )
            #draw a rectangle of dimensions 100x100 at the coordinates created above
            pygame.draw.rect(screen, SAFE_COLOR, pygame.Rect(coords[0], coords[1], 100, 100))


def display_reset_move_button():
    rect = pygame.Rect(
        RESET_MOVE_COORDS[0],
        RESET_MOVE_COORDS[1],
        RESET_MOVE_DIMS[0],
        RESET_MOVE_DIMS[1],
    )
    pygame.draw.rect(screen, BLACK, rect)
    screen.blit(font.render("Reset move?", True, WHITE), RESET_MOVE_COORDS)


def display_image(
    screen: pygame.Surface,
    itemStr: str,
    dimensions: Tuple[int, int],
    position: Tuple[int, int],
):
    """
    Draw an image on the screen at the indicated position.
    """
    v = pygame.image.load(itemStr).convert_alpha()
    v = pygame.transform.scale(v, dimensions)
    screen.blit(v, position)


def build_grid(GameBoard: Board):
    """
    Draw the grid on the screen.
    """

    grid_width = GameBoard.columns * GameBoard.display_cell_dimensions[0]
    grid_height = GameBoard.rows * GameBoard.display_cell_dimensions[1]
    # left
    pygame.draw.rect(
        screen,
        BLACK,
        [
            GameBoard.display_border - LINE_WIDTH,
            GameBoard.display_border - LINE_WIDTH,
            LINE_WIDTH,
            grid_height + (2 * LINE_WIDTH),
        ],
    )
    # right
    pygame.draw.rect(
        screen,
        BLACK,
        [
            GameBoard.display_border + grid_width,
            GameBoard.display_border - LINE_WIDTH,
            LINE_WIDTH,
            grid_height + (2 * LINE_WIDTH),
        ],
    )
    # bottom
    pygame.draw.rect(
        screen,
        BLACK,
        [
            GameBoard.display_border - LINE_WIDTH,
            GameBoard.display_border + grid_height,
            grid_width + (2 * LINE_WIDTH),
            LINE_WIDTH,
        ],
    )
    # top
    pygame.draw.rect(
        screen,
        BLACK,
        [
            GameBoard.display_border - LINE_WIDTH,
            GameBoard.display_border - LINE_WIDTH,
            grid_width + (2 * LINE_WIDTH),
            LINE_WIDTH,
        ],
    )
    # Fill the inside wioth the cell color
    pygame.draw.rect(
        screen,
        CELL_COLOR,
        [GameBoard.display_border, GameBoard.display_border, grid_width, grid_height],
    )
    #Draw the safe space so that it is under the lines
    display_safe_space(GameBoard)
    # Draw the vertical lines
    i = GameBoard.display_border + GameBoard.display_cell_dimensions[0]
    while i < GameBoard.display_border + grid_width:
        pygame.draw.rect(
            screen, BLACK, [i, GameBoard.display_border, LINE_WIDTH, grid_height]
        )
        i += GameBoard.display_cell_dimensions[0]
    # Draw the horizontal lines
    i = GameBoard.display_border + GameBoard.display_cell_dimensions[1]
    while i < GameBoard.display_border + grid_height:
        pygame.draw.rect(
            screen, BLACK, [GameBoard.display_border, i, grid_width, LINE_WIDTH]
        )
        i += GameBoard.display_cell_dimensions[1]


def display_people(GameBoard: Board):
    """
    Draw the people (government, vaccinated, and zombies) on the grid.
    """
    for x in range(len(GameBoard.States)):
        if GameBoard.States[x].person != None:
            p = GameBoard.States[x].person
            char = "Assets/person_normal.png"
            if p.isZombie:
                char = "Assets/person_zombie.png"
            elif p.isVaccinated:
                char = "Assets/person_vax.png"
            coords = (
                int(x % GameBoard.rows) * GameBoard.display_cell_dimensions[0]
                + GameBoard.display_border
                + 35,
                int(x / GameBoard.columns) * GameBoard.display_cell_dimensions[1]
                + GameBoard.display_border
                + 20,
            )
            display_image(screen, char, (35, 60), coords)
            if p.hasMed == True:
                display_image(screen, "Assets/RedCross.png", (20, 20), (coords[0]+25, coords[1]))

#Creates buttons that allow the player to quit or restart
def display_win_screen():
    restart_text = font.render('PLAY AGAIN', True, WHITE)
    quit_text = font.render('QUIT', True, WHITE)
    screen.fill(BACKGROUND)
    screen.blit(
        font.render("You win!", True, WHITE),
        (500, 350),
    )
    screen.blit(
        font.render("There were no possible moves for the computer.", True, WHITE),
        (500, 400),
    )
    
    while True:
        mouse = pygame.mouse.get_pos()
        pygame.draw.rect(screen,BLACK,[500,450,200,100])
        pygame.draw.rect(screen,BLACK,[500,600,200,100])
        screen.blit(restart_text, (550, 475))
        screen.blit(quit_text, (570, 625))
        for i in pygame.event.get():
            if i.type == pygame.MOUSEBUTTONDOWN:
                if 500 <= mouse[0] <= 700 and 450 <= mouse[1] <= 550:
                    return True
                elif 500 <= mouse[0] <= 700 and 600 <= mouse[1] <= 700:
                        return False
                        break
        pygame.display.update()

    # catch quit event
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

#similar code, just for a loss case
def display_lose_screen():
    restart_text = font.render('PLAY AGAIN', True, WHITE)
    quit_text = font.render('QUIT', True, WHITE)

    screen.fill(BACKGROUND)
    screen.blit(
        font.render("You lose!", True, WHITE),
        (500, 350),
    )
    screen.blit(
        font.render("You had no possible moves...", True, WHITE),
        (500, 400),
    )

    while True:
        mouse = pygame.mouse.get_pos()
        pygame.draw.rect(screen,BLACK,[500,450,200,100])
        pygame.draw.rect(screen,BLACK,[500,600,200,100])
        screen.blit(restart_text, (550, 475))
        screen.blit(quit_text, (570, 625))
        for i in pygame.event.get():
            if i.type == pygame.MOUSEBUTTONDOWN:
                if 500 <= mouse[0] <= 700 and 450 <= mouse[1] <= 550:
                    return True
                elif 500 <= mouse[0] <= 700 and 600 <= mouse[1] <= 700:
                        return False
                        break
        pygame.display.update()

    # catch quit event
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

def direction(coord1: Tuple[int, int], coord2: Tuple[int, int]):    
    if coord1 == coord2:
        return Direction.self
    elif coord2[1] > coord1[1]:
        return Direction.down
    elif coord2[1] < coord1[1]:
        return Direction.up
    elif coord2[0] > coord1[0]:
        return Direction.right
    elif coord2[0] < coord1[0]:
        return Direction.left
