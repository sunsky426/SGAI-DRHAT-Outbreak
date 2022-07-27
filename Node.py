import numpy as np
from collections import defaultdict


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


