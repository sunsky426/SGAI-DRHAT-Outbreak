#from sys import setdlopenflags
import numpy as np
from collections import defaultdict
from Board import Board
from constants import *


class Node:
    def __init__(self, state: Board, parent=None, parent_action=None, age = 0):
        self.state = state  # the board state
        self.parent = parent # whatever node this node came from, root node has no parent
        self.parent_action = parent_action  # action which parent carried out, root node is none again
        self.children = []  # all possible actions from current node
        self.num_visits = 0 #how many times the node is visited
        self.results = defaultdict(int) #has all the possible results of a game, but for ours its only win or lose, so 1 or -1
        self.results[1] = 0 #starts with 0 wins
        self.results[-1] = 0  # starts with 0 losses
        #self.untried_actions = None #all possible actions
        self.untried_actions = self.untried_actions()
        self.age = age
        return

    def untried_actions(self): #starts with all possible actions, then is shrunk later in the expand function
        self.untried_actions = self.state.get_legal_actions()
        return self.untried_actions

    def q(self): #returns wins - losses of all of the children (I think)
        wins = self.results[1]
        losses = self.results[-1]
        return wins - losses

    def n(self):
        return self.num_visits
    
    def expand(self):
        start, action, direction, target = self.untried_actions.pop() #takes an action from untried actions
        next_state = self.state.act[action](start, direction) #creates the state after that move happens
        child_node = Node(next_state, parent=self, parent_action=(start, action, direction, target), age=self.age+1) #creates a node with that state and action as a child of this node
        self.children.append(child_node) #adds that node to the children of this node
        return child_node #returns the child node
    
    def is_terminal_node(self): #checks if this is the last node in the branch
        return self.state.is_game_over()

    def rollout(self):
        current_rollout_state = self.state 
        while not current_rollout_state.is_game_over(): #while the node is not a terminal node
            possible_moves = current_rollout_state.get_legal_actions() #get all moves from this node
            action = self.rollout_policy(possible_moves) #select a move using the rollout policy (random by default)
            current_rollout_state = current_rollout_state.NodeMove(action) #change the node to the state after said action is made
        return current_rollout_state.game_result() #loop the above until the game ends, then return the game result
    
    def backpropagate(self, result): #send the information from the node back to the root
        self.num_visits += 1. #adds number of visits to all the nodes above
        self.results[result] += 1. #adds the result of the terminal node to the dictionary of all possible results
        if self.parent is not None:
            self.parent.backpropagate(result) # recursion
    
    def is_fully_expanded(self):
        return len(self.untried_actions) == 0 #if there are no actions possible (this stops making children i think)

    def best_child(self, c_param=0.1): #returns the best child from this node
        choices_weights = [(c.q() / c.n()) + c_param * np.sqrt((2 * np.log(self.n()) / c.n())) for c in self.children] #calculates the 'value' of each child
        return self.children[np.argmax(choices_weights)] #returns the child that corrosponds to the highest value in the above list
    
    def rollout_policy(self, possible_moves): #how to select a move, currently random but I think we change it later
        return possible_moves[np.random.randint(len(possible_moves))]

    def _tree_policy(self): #branches every node
        current_node = self
        while not current_node.is_terminal_node() and self.age < 5: #while selected node is not the last node
            if not current_node.is_fully_expanded(): # if the selected node hasnt been fully expanded, expand it
                return current_node.expand()
            else:
                current_node = current_node.best_child() #if it has been expanded, return the image.pngbest node of the children
        return current_node #in the end, return the best node of all of the children of this node, this is the mcts program basically
    
    def best_action(self): #pretty self explanatory
        simulation_no = 100  
        for i in range(simulation_no): #creates simulations
            v = self._tree_policy() #makes all the nodes
            reward = v.rollout() #does the moves for all the nodes
            v.backpropagate(reward) #send all the info back to the root
        return self.best_child(c_param=0.) #return the best node for the root to choose

    def game_result(self, board):
        """
        Should return a reward value based on the result of the game
        Either a positive value when humans win, based on how many people remain, or a negative value when zombies win
        """
        reward = 0
        if self.game_ended():
            # checks if the game has ended before returning a reward value other than 0
            for s in board.States:
                # this code has been written based on the assumption that that the state will be defined as Gameboard.states
                if s.person == True and s.person.isZombie == False:
                    reward += 1
                
            if reward == 0:
                # returns a basic value of -10 whenever the zombies win, can be changed later
                reward = -10
        else:
            return self.board_eval()
        return reward

    def game_ended(self):
        return self.state.num_zombies() == self.state.population or self.state.num_zombies() == 0

    def add_children(self):
        """
        This is technically "move" but I may write another move function where the AI actually chooses a node,
        since this one just adds all the child nodes to the children array.
        """
        if not self.game_ended():  # if this node isnt a terminal node
            for i in self.untried_actions:  # looking through neighboring states and creating nodes off of that
                c = Node(i, self, self.state, age = self.age + 1)  # make da node
                self.children.append(c)  # add child to list
        return self.children  # return list of children (idk if return statement is needed)

    def board_eval(self):
        zombie_count = 0
        human_count = 0
        for state in self.state.States:
            if state.person is not None:
                if state.person.isZombie:
                    zombie_count += 1
                else:
                    human_count += 1
            
        return (human_count- 0.9*zombie_count - 0.05 * self.state.outrage)
