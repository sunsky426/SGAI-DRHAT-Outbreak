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

        #stores all people or zombies on a board
        agents = []
        if GameBoard.player_role == Role.government:
            agents = self.get_possible_states(1, False)
        elif GameBoard.player_role == Role.zombie:
            agents = self.get_possible_states(-1, True)

        for agent in agents: 
            possible_move_coords = GameBoard.get_possible_moves(
                            action, direction, computer_role
                        )

        return legal_actions 
