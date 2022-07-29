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

    def game_result(self):
        """
        Should return a reward value based on the result of the game
        Either a positive value when humans win, based on how many people remain, or a negative value when zombies win
        """
        reward = 0
        if not self.gameRunning:
            # checks if the game has ended before returning a reward value other than 0
            for s in state:
                # this code has been written based on the assumption that that the state will be defined as Gameboard.states
                if s.person == True and s.person.isZombie == False:
                    reward += 1
                else:
                    # returns a basic value of -10 whenever the zombies win, can be changed later
                    reward = -10
        return reward

    def game_ended(self):
        self.gameRunning = False

    def add_children(self):
        """
        This is technically "move" but I may write another move function where the AI actually chooses a node,
        since this one just adds all the child nodes to the children array.
        """
        if self.gameRunning:  # if this node isnt the terminal node
            for i in self.untried_actions:  # looking through neighboring states and creating nodes off of that
                c = Node(i, self, self.state)  # make da node
                self.children.append(c)  # add child to list
        return self.children  # return list of children (idk if return statement is needed)
