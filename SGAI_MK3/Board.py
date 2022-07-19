from tracemalloc import start
from State import State
import random as rd
from Person import Person
from typing import Tuple


class Board:
    #initializing variables
    States = []
    QTable = []
    rows = 0
    columns = 0
    population = 0   # total number of people and zombies
    Player_Role = 0  # 1 if gov't, -1 if zombies
    action_space = ["moveUp", "moveDown", "moveLeft", "moveRight", "heal", "bite"] #all possible moves for zombies and people

    def __init__(self, dimensions, pr):  
        self.rows = dimensions[0]
        self.columns = dimensions[1]
        self.Player_Role = pr 
        for s in range(dimensions[0] * dimensions[1]):# creates a 1d array of the board
            self.States.append(State(None, s))
            self.QTable.append([0] * 6)

        self.actionToFunction = { #makes it so that the action_space contents can directly correlate to functions
            "moveUp": self.moveUp,
            "moveDown": self.moveDown,
            "moveLeft": self.moveLeft,
            "moveRight": self.moveRight,
            "heal": self.heal,
            "bite": self.bite,
        }

    def num_zombies(self): #number of zombies on the board, different than population
        r = 0
        for state in self.States:
            if state.person != None:
                if state.person.isZombie:
                    r += 1
        return r

    def act(self, oldstate, givenAction): # takes in the cell and action and performs that using the actiontofunction
        cell = self.toCoord(oldstate)
        f = self.actionToFunction[givenAction](cell)
        reward = self.States[oldstate].evaluate(givenAction, self)
        if f[0] == False:
            reward = 0
        return [reward, f[1]]

    def containsPerson(self, isZombie): #checks if person is a person
        for state in self.States:
            if state.person is not None and state.person.isZombie == isZombie:
                return True
        return False

    def get_possible_moves(self, action, role):
        """
        Get the coordinates of people (or zombies) that are able
        to make the specified move.
        @param action - the action to return possibilities for (options are 'bite', 'moveUp', 'moveDown','moveLeft', 'moveRight', and 'heal')
        @param role - either 'Zombie' or 'Government'; helps decide whether an action
        is valid and which people/zombies it applies to
        """
        poss = []
        B = self.clone(self.States, self.Player_Role)

        if role == "Zombie":
            if not self.containsPerson(True):
                return poss
            for idx in range(len(self.States)): #goes through all the boxes
                state = self.States[idx]
                if state.person is not None: # checks if a box is empty
                    changed_states = False
                    if (
                        action == "bite"
                        and not state.person.isZombie
                        and self.isAdjacentTo(self.toCoord(idx), True)
                    ):
                        # if the current space isn't a zombie and it is adjacent to a space that is a zombie, it can bite
                        poss.append(B.toCoord(state.location))
                        changed_states = True
                    elif ( # otherwise move
                        state.person.isZombie
                        and B.actionToFunction[action](B.toCoord(state.location))[0]
                    ):
                        poss.append(B.toCoord(state.location))
                        changed_states = True

                    if changed_states:
                        # reset the states because it had to check the possible moves by moving the states
                        B.States = [
                            self.States[i].clone()
                            if self.States[i] != B.States[i]
                            else B.States[i]
                            for i in range(len(self.States))
                        ]

        elif role == "Government":
            if not self.containsPerson(False): #if theres no one on the board then no possible moves
                return poss
            for state in self.States:
                if state.person is not None: #checks if the boxes are empty
                    changed_states = False
                    if (
                        action == "heal" # checks if it can heal
                        and state.person.isZombie
                        or not state.person.isVaccinated
                        or not state.person.wasCured
                    ):
                        poss.append(B.toCoord(state.location))
                        changed_states = True
                    elif ( # otherwise move
                        not state.person.isZombie
                        and B.actionToFunction[action](B.toCoord(state.location))[0]
                    ):
                        poss.append(B.toCoord(state.location))
                        changed_states = True

                    if changed_states:
                        # reset the states cuz it moved the board to check possibilities
                        B.States = [
                            self.States[i].clone()
                            if self.States[i] != B.States[i]
                            else B.States[i]
                            for i in range(len(self.States))
                        ]

        print("possible: ", poss)
        return poss

    def toCoord(self, i): # converts coord from 1d to 2d
        return (int(i % self.columns), int(i / self.rows))

    def toIndex(self, coordinates): # converts coord from 2d to 1d
        return int(coordinates[1] * self.columns) + int(coordinates[0])

    def isValidCoordinate(self, coordinates): #checks if the box is in the grid
        return (
            coordinates[1] < self.rows
            and coordinates[1] >= 0
            and coordinates[0] < self.columns
            and coordinates[0] >= 0
        )

    def clone(self, L: list, role): #creates a duplicate board
        NB = Board((self.rows, self.columns), role)
        NB.States = [state.clone() for state in L]
        NB.Player_Role = role
        return NB

    def isAdjacentTo(self, coord, is_zombie: bool) -> bool: # returns adjacent coordinates containing the same type (so person if person etc)
        ret = False
        vals = [
            (coord[0], coord[1] + 1),
            (coord[0], coord[1] - 1),
            (coord[0] + 1, coord[1]),
            (coord[0] - 1, coord[1]),
        ]
        for coord in vals:
            if (
                self.isValidCoordinate(coord)
                and self.States[self.toIndex(coord)].person is not None
                and self.States[self.toIndex(coord)].person.isZombie == is_zombie
            ):
                ret = True
                break

        return ret

    def move(self, from_coords, new_coords) -> Tuple[bool, int]: #returns (if the move could be done, destination coord)
        start_idx = self.toIndex(from_coords)
        destination_idx = self.toIndex(new_coords)

        if not self.isValidCoordinate(new_coords):
            return [False, destination_idx]

        try:
            # only allow a move if the space isn't already occupied
            if self.States[destination_idx].person is None:
                self.States[destination_idx].person = self.States[start_idx].person
                self.States[start_idx].person = None
                return [True, destination_idx]
            return [False, destination_idx]
        except:
            return [False, destination_idx]

    #following functions just clone the destination square and clear the starter square, returning if the move was successful and the destination

    def moveUp(self, coords) -> Tuple[bool, int]:
        new_coords = (coords[0], coords[1] - 1)
        print(f"going from {coords} to new coords {new_coords}")
        return self.move(coords, new_coords)

    def moveDown(self, coords) -> Tuple[bool, int]:
        new_coords = (coords[0], coords[1] + 1)
        print(f"going from {coords} to new coords {new_coords}")
        return self.move(coords, new_coords)

    def moveLeft(self, coords) -> Tuple[bool, int]:
        new_coords = (coords[0] - 1, coords[1])
        print(f"going from {coords} to new coords {new_coords}")
        return self.move(coords, new_coords)

    def moveRight(self, coords) -> Tuple[bool, int]:
        new_coords = (coords[0] + 1, coords[1])
        print(f"going from {coords} to new coords {new_coords}")
        return self.move(coords, new_coords)

    # q learning functions

    def QGreedyat(self, state_id): #evaluates the best move in the qtable, returning the index of the move in the table and the move
        biggest = self.QTable[state_id][0] * self.Player_Role
        ind = 0
        A = self.QTable[state_id]
        i = 0
        for qval in A:
            if (qval * self.Player_Role) > self.biggest:
                biggest = qval
                ind = i
            i += 1
        return [ind, self.QTable[ind]]  # action_index, qvalue

    # picks the action for the move in the qtable, including a probability that it is randomized based on the learning rate
    def choose_action(self, state_id, lr):
        L = lr * 100
        r = rd.randint(0, 100)
        if r < L:
            return self.QGreedyat(state_id)
        else:
            if self.Player_Role == 1:  # Player is Govt
                d = rd.randint(0, 4)
            else:
                d = rd.randint(0, 5)
                while d != 4:
                    d = rd.randint(0, 4)
            return d

    # picks the person that it wants to move or use, also including a learning rate based probability, returning the index of the state
    def choose_state(self, lr):
        L = lr * 100
        r = rd.randint(0, 100)
        if r < L:
            biggest = None
            sid = None
            for x in range(len(self.States)):
                if self.States[x].person != None:
                    q = self.QGreedyat(x)
                    if biggest is None:
                        biggest = q[1]
                        sid = x
                    elif q[1] > biggest:
                        biggest = q[1]
                        sid = x
            return self.QGreedyat(sid)
        else:
            if self.Player_Role == -1:  # Player is Govt
                d = rd.randint(0, len(self.States))
                while self.States[d].person is None or self.States[d].person.isZombie:
                    d = rd.randint(0, len(self.States))
            else:
                d = rd.randint(0, len(self.States))
                while (
                    self.States[d].person is None
                    or self.States[d].person.isZombie == False
                ):
                    d = rd.randint(0, len(self.States))
            return d


    # defining the actions of the persons

    def bite(self, coords):
        i = self.toIndex(coords)
        if self.States[i] is None:
            return False
        chance = 100
        p = self.States[i].person
        if p.isVaccinated:
            chance = 0
        elif p.wasVaccinated != p.wasCured:
            chance = 75
        elif p.wasVaccinated and p.wasCured:
            chance = 50
        r = rd.randint(0, 100)
        if r < chance:
            newP = p.clone()
            newP.isZombie = True
            self.States[i].person = newP
        return [True, i]

    def heal(self, coords):
        i = self.toIndex(coords)
        if self.States[i].person is None:
            return False
        p = self.States[i].person
        newP = p.clone()
        newP.isZombie = False
        if newP.wasCured == False:
            newP.wasCured = True
        if newP.isVaccinated == False:
            newP.isVaccinated = True
            newP.turnsVaccinated = 1
        self.States[i].person = newP
        return [True, i]

    #gets all the locations of people or zombies on the board (this can be used to count them as well)
    def get_possible_states(self, rn):
        indexes = []
        i = 0
        for state in self.States:
            if state.person != None:
                if rn == 1 and state.person.isZombie == False:
                    indexes.append(i)
                elif rn == -1 and state.person.isZombie:
                    indexes.append(i)
            i += 1
        return indexes

    # runs each choice for the qlearning algorithm
    def step(self, role_number, learningRate):
        P = self.get_possible_states(role_number) #gets all the relevent players
        r = rd.uniform(0, 1)
        if r < learningRate: # 50% chance of this happening
            rs = rd.randrange(0, len(self.States) - 1)
            if role_number == 1:
                while (
                    self.States[rs].person is not None
                    and self.States[rs].person.isZombie
                ):                                                  #picks a relevent person, but idk why its not via all the possible people 
                    rs = rd.randrange(0, len(self.States) - 1)      #and instead searches all the states again
            else:
                while (
                    self.States[rs].person is not None
                    and self.States[rs].person.isZombie == False    #same thing but for zombie
                ):
                    rs = rd.randrange(0, len(self.States) - 1)

            # random state and value
        # old_value = QTable[state][acti]
        # next_max = np.max(QTable[next_state])
        # new_value = (1 - alpha) * old_value + alpha * (reward + gamma * next_max)
        # QTable[state][acti] = new_value

    #adds the people into the grid
    def populate(self):
        total = rd.randint(7, ((self.rows * self.columns) / 3)) # adds between 7 and squares/3 (12 rn) people
        poss = []
        for x in range(len(self.States)): # 60% chance that there will be a person in a square, which stupidly weighs them towards the top
            r = rd.randint(0, 100)
            if r < 60 and self.population < total: 
                p = Person(False)
                self.States[x].person = p
                self.population = self.population + 1
                poss.append(x)
            else:
                self.States[x].person = None
        print("people at ", poss)
        used = []
        for x in range(4):                     # adds four zombies every time, so worst case there will be 3 ppl and 4 zombies
            s = rd.randint(0, len(poss) - 1)   # and the best case scenario is 8 ppl 4 zombies
            while s in used:
                s = rd.randint(0, len(poss) - 1)
            self.States[poss[s]].person.isZombie = True
            used.append(s)
