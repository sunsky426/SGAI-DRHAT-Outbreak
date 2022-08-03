from hashlib import new
import pygame
from Board import Board
from Node import Node
import PygameFunctions as PF
import random as rd
from constants import *
import time
from Node import *

# Player role variables
player_role = Role.government  # Valid options are Role.government and Role.zombie
roleToRoleNum = {Role.government: 1, Role.zombie: -1}

# Create the game board
GameBoard = Board((ROWS, COLUMNS), BORDER, CELL_DIMENSIONS, player_role)
GameBoard.populate()
root_node = Node(GameBoard,None, None) # make root note

# Self play variables
alpha = 0.1
gamma = 0.6
epsilon = 0.1
epochs = 1000
epochs_ran = 0
Original_Board = GameBoard.clone(GameBoard.States, GameBoard.player_role)


# Initialize variables
running = True
take_action = []
playerMoved = False
font = pygame.font.SysFont("Comic Sans", 20)
start = False

#Initial player score
player_score = 0

Data = [[[], [], [], [], [], []]] #[[kills], [heals], [meds], [zombies/population], [anxiety], [outrage]]
Turn = 0

while running:
    #displays the main menu until user hits start or quit
    if start == False:
        try:
            start = PF.disp_title_screen()
        #Throws exception when user quits program using in-game button
        except pygame.error:
            print("Data: ", Data)
            print("Game closed by user")
            break
    elif start == True:
        P = PF.run(GameBoard)


        if SELF_PLAY:
            if( #if the game is over
                not GameBoard.containsPerson(bool(player_role.value))
                or GameBoard.outrage >= 100
            ):
                #node.game_ended()
                running = PF.display_lose_screen()
                for state in GameBoard.States:
                    state.person = None
                    state.safeSpace = False
                GameBoard.populate()
                start = False
                Data.append([[], [], [], [], [], []])
                Turn = 0   
                continue
            # Event Handling
            for event in P:
                if event.type == pygame.MOUSEBUTTONUP:
                    x, y = pygame.mouse.get_pos()
                    action = PF.get_action(GameBoard, x, y)
                    if(action == "Distrb Med"):
                        take_action.append("Distrb Med")
                        Data[-1][2].append(Turn)
                        time.sleep(0.1)
                        GameBoard.med()
                        take_action = []
                    
                    elif(
                        type(action) == Action
                        and len(take_action) == 0
                    ):
                        # only allow healing by itself (prevents things like ['move', (4, 1), 'heal'])
                        take_action.append(action)

                    elif action == "reset move":
                        take_action = []
                    elif action == "ai turn":
                        #pick the AI move
                        #best_child = root_node.best_action() #find the best child of the root node
                        GameBoard.allowclicks = False
                        GameBoard = root_node.best_action().state
                        root_node = Node(GameBoard,None, None) # make root note
                        #root_node = best_child
                        print("AI Moved")
                        
                    elif type(action) is tuple:
                        idx = GameBoard.toIndex(action)
                        # action is a coordinate
                        if idx < (GameBoard.rows * GameBoard.columns) and idx > -1:
                            if Action.move not in take_action and len(take_action) == 0:
                                # make sure that the space is not an empty space or a space of the opposite team
                                # since cannot start a move from those invalid spaces
                                if (
                                    GameBoard.States[idx].person is not None
                                    and GameBoard.States[idx].person.isZombie
                                    == bool(player_role.value)
                                ):
                                    take_action.append(Action.move)
                                else:
                                    continue


                            take_action.append(action)
                if event.type == pygame.QUIT:
                    running = False

            # Display the current action
            PF.screen.blit(
                font.render("Your move is currently:", True, PF.WHITE),
                (800, 400),
            )
            PF.screen.blit(font.render(f"{take_action}", True, PF.WHITE), (800, 450))

            

            # Action handling
            if len(take_action) > 2:
                    directionToMove = PF.direction(take_action[1], take_action[2])
                    print("Implementing", take_action[0], "to", directionToMove)
                    result = GameBoard.act[take_action[0]](take_action[1], directionToMove)
                    print(f"did it succeed? {result}")

                    if result == Result.success:
                        player_score += PF.get_reward(take_action[0])
                        #if it succeeds, the player gets a reward corresponding to their action
                        if take_action[0] == Action.kill: #add to data
                            Data[-1][0].append(Turn)
                        elif take_action[0] == Action.heal:
                            Data[-1][1].append(Turn)
                        Data[-1][3].append(round(GameBoard.num_zombies()/GameBoard.population, 2))
                        Data[-1][4].append(GameBoard.anxiety)
                        Data[-1][5].append(GameBoard.outrage)
                    if result != Result.invalid:
                        playerMoved = True
                    take_action = []
            #Display the player's current score
            PF.screen.blit(font.render("Score: " + str(player_score), True, PF.WHITE),(900,500))

            if playerMoved:
                Turn+=1

                # Intermission
                PF.run(GameBoard)
                pygame.display.update()
                time.sleep(0.1)
                print("Enemy turn")

                # Computer turn
                playerMoved = False
                take_action = []

                #if player_role == Role.government:
                #    possible_actions = [Action.move, Action.bite]
                #    computer_role = Role.zombie
                #else:
                ##    possible_actions = [Action.move, Action.heal, Action.kill]
                #    computer_role = Role.government

                computer_role = Role.zombie
                possible_act_coords = []

                #check if possible to bite
                action = Action.bite
                possible_direction = [member for name, member in Direction.__members__.items()]
                while len(possible_act_coords) == 0 and len(possible_direction) != 0:
                        direction = rd.choice(possible_direction)
                        possible_direction.remove(direction)
                        possible_act_coords = GameBoard.get_possible_moves(
                            action, direction, computer_role
                        )
                
                if len(possible_act_coords) == 0:
                    #try moving a zombie close enough to player
                    action = Action.move
                    human_coords = []
                    zombie_coords = []
                    best_dist = float("inf")

                    for idx in range(len(GameBoard.States)):
                        state = GameBoard.States[idx]
                        if state.person is not None:
                            if state.person.isZombie == True:
                                zombie_coords.append(GameBoard.toCoord(idx))
                            else:
                                human_coords.append(GameBoard.toCoord(idx))
                        
                        for zombie in zombie_coords:
                            for victim in human_coords:
                                dist = (zombie[0] - victim[0])**2 + (zombie[1] - victim[1])**2
                                if dist < best_dist:
                                    dir = PF.direction(zombie, victim)
                                    B = GameBoard.clone(GameBoard.States, computer_role)
                                    bruh = B.act[Action.move](zombie, dir)
                                    if bruh != Result.invalid:
                                        print(bruh)
                                        direction = dir
                                        best_dist = dist
                                        possible_act_coords = []
                                        possible_act_coords.append(zombie)
                                        print("WOW", zombie, victim, dir)
                    
                    if len(possible_act_coords) == 0:
                        #just make a random move
                        possible_direction = [member for name, member in Direction.__members__.items()]
                        action = Action.move
                        #cycles through directions
                        while len(possible_act_coords) == 0 and len(possible_direction) != 0:
                            direction = rd.choice(possible_direction)
                            possible_direction.remove(direction)
                            possible_act_coords = GameBoard.get_possible_moves(
                                action, direction, computer_role
                            )

                # no valid moves, player wins
                #Displays two buttons and allows the player to play again on a new randomized map
                if (
                    len(possible_direction) == 0
                    and len(possible_act_coords) == 0
                ):
                    running = PF.display_win_screen()
                    for state in GameBoard.States:
                        state.person = None
                        state.safeSpace = False
                    GameBoard.populate()
                    start = False
                    continue

                # Select the destination coordinates
                move_coord = rd.choice(possible_act_coords)

                # Implement the selected action
                print(action, direction, move_coord)
                print(GameBoard.act[action](move_coord, direction))
                print("stopping")

        # Update the display
        pygame.display.update()
        pygame.time.wait(75)

    else:
        if epochs_ran % 100 == 0:
            print("Board Reset!")
            GameBoard = Original_Board  # reset environment
        for event in P:
            i = 0
            r = rd.uniform(0.0, 1.0)
            st = rd.randint(0, len(GameBoard.States) - 1)
            state = GameBoard.QTable[st]

            if r < gamma:
                while GameBoard.States[st].person is None:
                    st = rd.randint(0, len(GameBoard.States) - 1)
            else:
                biggest = None
                for x in range(len(GameBoard.States)):
                    arr = GameBoard.QTable[x]
                    exp = sum(arr) / len(arr)
                    if biggest is None:
                        biggest = exp
                        i = x
                    elif biggest < exp and player_role == Role.government:
                        biggest = exp
                        i = x
                    elif biggest > exp and player_role != Role.government:
                        biggest = exp
                        i = x
                state = GameBoard.QTable[i]
            b = 0
            j = 0
            ind = 0
            for v in state:
                if v > b and player_role == Role.government:
                    b = v
                    ind = j
                elif v < b and player_role != Role.government:
                    b = v
                    ind = j
                j += 1
            action_to_take = ACTION_SPACE[ind]
            old_qval = b
            old_state = i

            # Update
            # Q(S, A) = Q(S, A) + alpha[R + gamma * max_a Q(S', A) - Q(S, A)]
            reward = GameBoard.act(old_state, action_to_take)
            ns = reward[1]
            NewStateAct = GameBoard.QGreedyat(ns)
            NS = GameBoard.QTable[ns][NewStateAct[0]]
            # GameBoard.QTable[i] = GameBoard.QTable[i] + alpha * (reward[0] + gamma * NS) - GameBoard.QTable[i]
            if GameBoard.num_zombies() == 0:
                print("winCase")

            take_action = []
            print("Enemy turn")
            ta = ""
            if player_role == Role.government:
                r = rd.randint(0, 5)
                while r == 4:

                    r = rd.randint(0, 5)
                    while r == 4:
                        r = rd.randint(0, 5)
                    ta = ACTION_SPACE[r]
                else:
                    r = rd.randint(0, 4)
                    ta = ACTION_SPACE[r]
                poss = GameBoard.get_possible_moves(ta, Role.zombie)

                if len(poss) > 0:
                    r = rd.randint(0, len(poss) - 1)
                    a = poss[r]
                    GameBoard.act[ta](a)
                if GameBoard.num_zombies() == GameBoard.population:
                    print("loseCase")
                if event.type == pygame.QUIT:
                    running = False
print("Data: ", Data)
pygame.display.quit()