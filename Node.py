import numpy as np
from collections import defaultdict
from constants import Role
from Board import *

class Node:
    def __init__(self, state, parent=None, parent_action=None):
        self.state = state  # human or zombie? dead or alive? vaxxed or unvaxxed?
        self.parent = parent
        self.parent_action = parent_action  # action which parent carried out, none for root node (since no parent)
        self.children = []  # all possible actions from current node
        self.num_visits = 0
        self.results = defaultdict(int)
        self.results[1] = 0
        self.results[-1] = 0  # idk what those three lines do...
        self.untried_actions = None
        self.untried_actions = self.untried_actions()
        self.gameRunning = True
        return

    def game_ended(self):
        self.gameRunning = False

    
    def get_legal_actions(self, GameBoard): 
        legal_actions = [] 
        actors = []

        #based on role, get positions of all actors 
        # and define possible actions
        if GameBoard.player_role == Role.government:
            actors = self.get_possible_states(1)
            possible_actions = [Action.move, Action.heal, Action.kill]
        elif GameBoard.player_role == Role.zombie:
            actors = self.get_possible_states(-1)
            possible_actions = [Action.move, Action.bite]
 
        possible_directions = [member for name, member in Direction]

        #iterate through all states on board
        for state in GameBoard.States:

            if state.person != None:
                #get adjacent squares
                move_space = state.adjacent(GameBoard)
                if (GameBoard.player_role == Role.government 
                    and not state.person.isZombie):

                    #attempt to move into valid squares, see if it works
                    for target in move_space:
                        for direction in possible_directions:
                            result = GameBoard.move_validity(target, direction)
                            if not result == Result.invalid:
                                #if valid, add the action to the list
                                legal_actions.append((state, Action.move, direction, target))

                            #repeat, but with healing
                            result = GameBoard.heal_validity(target, direction)
                            if not result == Result.invalid:
                                #if valid, add the action to the list
                                legal_actions.append((state, Action.heal, direction, target))
                        
                            #repeat, but with killing
                            result = GameBoard.heal_validity(target, direction)
                            if not result == Result.invalid:
                                #if valid, add the action to the list
                                legal_actions.append((state, Action.kill, direction, target))

                if (GameBoard.player_role == Role.zombie 
                    and state.person.isZombie):

                    #attempt to move into valid squares, see if it works
                    for target in move_space:
                        for direction in possible_directions:
                            result = GameBoard.move_validity(target, direction)
                            if not result == Result.invalid:
                                #if valid, add the action to the list
                                legal_actions.append((state, Action.move, direction, target))

                            #repeat, but with biting
                            result = GameBoard.bite_validity(target, direction)
                            if not result == Result.invalid:
                                #if valid, add the action to the list
                                legal_actions.append((GameBoard.toCoord(state.location), Action.bite, direction, target))
                                
        return legal_actions
        