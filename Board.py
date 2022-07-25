from State import State
import random as rd
from Person import Person
from typing import List, Tuple
from Constants import *


class Board:
    #initializing variables
    def __init__(
        self,
        dimensions: Tuple[int, int],
        border: int,
        cell_dimensions: Tuple[int, int],
        player_role: Role,
    ):
        self.rows = dimensions[0]
        self.columns = dimensions[1]
        self.display_border = border
        self.display_cell_dimensions = cell_dimensions
        self.player_role = player_role

        if player_role == Role.government:
            self.computer_role = Role.zombie
        else:
            self.computer_role = Role.government

        self.population = 0 # total number of people and zombies
        self.States = []
        self.QTable = []
        for s in range(dimensions[0] * dimensions[1]): # creates a 1d array of the board
            self.States.append(State(None, s))
            self.QTable.append([0] * 6)

        self.actionToFunction = {
            Action.move: self.move,
            Action.heal: self.heal,
            Action.bite: self.bite,
            Action.kill: self.kill
        }

    def num_zombies(self) -> int: #number of zombies on the board, different than population
        r = 0
        for state in self.States:
            if state.person != None:
                if state.person.isZombie:
                    r += 1
        return r

    def act(self, oldstate: Tuple[int, int], givenAction: str): # takes in the cell and action and performs that using the actiontofunction
        cell = self.toCoord(oldstate)
        f = self.actionToFunction[givenAction](cell)
        reward = self.States[oldstate].evaluate(givenAction, self)
        if f[0] == False:
            reward = 0
        return [reward, f[1]]

    def containsPerson(self, isZombie: bool): #checks if person is a person
        for state in self.States:
            if state.person is not None and state.person.isZombie == isZombie:
                return True
        return False

    def get_possible_moves(self, action: Action, direction: Direction, role):
        """
        Get the coordinates of people (or zombies) that are able
        to make the specified move.
        @param action - the action to return possibilities for (options are Action.bite, Action.move, Action.heal, and Action.kil)
        @param direction - the direction this action is heading (options are Direction.up, Direction.down, Direction.left, Direction.right)
        @param role - either 'Zombie' or 'Government'; helps decide whether an action
        is valid and which people/zombies it applies to
        """
        poss = []
        B = self.clone(self.States, role)

        if role == Role.zombie:
            if not self.containsPerson(True):
                return poss

            for state in self.States:
                if state.person is not None:
                    changed_states = False

                    if (
                        state.person.isZombie
                        and B.actionToFunction[action](B.toCoord(state.location), direction, role)[0]
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

        elif role == Role.government:
            if not self.containsPerson(False):

                return poss
            for state in self.States:
                if state.person is not None: #checks if the boxes are empty
                    changed_states = False
                    if (
                        not state.person.isZombie
                        and B.actionToFunction[action](B.toCoord(state.location), direction)[0]
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
        return poss

    def toCoord(self, i: int): # converts coord from 1d to 2d
        return (int(i % self.columns), int(i / self.rows))

    def toIndex(self, coordinates: Tuple[int, int]): # converts coord from 2d to 1d
        return int(coordinates[1] * self.columns) + int(coordinates[0])

    def isValidCoordinate(self, coordinates: Tuple[int, int]): #checks if the box is in the grid
        return (
            coordinates[1] < self.rows
            and coordinates[1] >= 0
            and coordinates[0] < self.columns
            and coordinates[0] >= 0
        )

    def clone(self, L: List[State], role: Role): #creates a duplicate board

        NB = Board(
            (self.rows, self.columns),
            self.display_border,
            self.display_cell_dimensions,
            self.player_role,
        )
        NB.States = [state.clone() for state in L]
        NB.player_role = role
        return NB

    def isAdjacentTo(self, coord: Tuple[int, int], is_zombie: bool) -> bool: # returns adjacent coordinates containing the same type (so person if person etc)

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

    def getTargetCoords(self, coords: Tuple[int, int], direction: Direction) -> Tuple[int, int]:
        if direction == Direction.up:
            new_coords = (coords[0], coords[1] - 1)
            print(f"going from {coords} to new coords {new_coords}")
        elif direction == Direction.down:
            new_coords = (coords[0], coords[1] + 1)
            print(f"going from {coords} to new coords {new_coords}")
        elif direction == Direction.left:
            new_coords = (coords[0] - 1, coords[1])
            print(f"going from {coords} to new coords {new_coords}")
        elif direction == Direction.right:
            new_coords = (coords[0] + 1, coords[1])
            print(f"going from {coords} to new coords {new_coords}")
        elif direction == Direction.self:
            new_coords = coords
        
        self.States[self.toIndex(coords)].person.facing = Direction

        return new_coords
    
    def move(self, coords: Tuple[int, int], direction: Direction, role: Role) -> Tuple[bool, int]:    
        new_coords = self.getTargetCoords(coords, direction)
        if direction == Direction.self: return (False, new_coords)
        if not self.isValidCoordinate(new_coords): return (False, new_coords)
        
        # Get the start and destination index (1D)
        start_idx = self.toIndex(coords)
        destination_idx = self.toIndex(new_coords)

        # Check if the new coordinates are valid
        if not self.isValidCoordinate(new_coords):
            return [False, destination_idx]
        if(
            role == Role.zombie
            and self.States[destination_idx].safeSpace
        ):
            return [False, destination_idx]

        # Check if the destination is currently occupied
        if self.States[destination_idx].person is None:
            #Execute Move
            self.States[destination_idx].person = self.States[start_idx].person
            self.States[start_idx].person = None
            return [True, destination_idx]
        return [False, destination_idx]

    def QGreedyat(self, state_id):
        biggest = self.QTable[state_id][0] * self.player_role
        ind = 0
        A = self.QTable[state_id]
        i = 0
        for qval in A:
            if (qval * self.player_role) > biggest:
                biggest = qval
                ind = i
            i += 1
        return [ind, self.QTable[ind]]  # action_index, qvalue

    # picks the action for the move in the qtable, including a probability that it is randomized based on the learning rate
    def choose_action(self, state_id: int, lr: float): 
        L = lr * 100
        r = rd.randint(0, 100)
        if r < L:
            return self.QGreedyat(state_id)
        else:
            if self.player_role == Role.government:  # Player is Govt
                d = rd.randint(0, 4)
            else:
                d = rd.randint(0, 5)
                while d != 4:
                    d = rd.randint(0, 4)
            return d

    # picks the person that it wants to move or use, also including a learning rate based probability, returning the index of the state
    def choose_state(self, lr: float):
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
            if self.player_role == Role.government:  # Player is Govt
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

    def bite(self, coords: Tuple[int, int], direction: Direction, role: Role) -> Tuple[bool, int]:
        target_coords = self.getTargetCoords(coords, direction)
        if direction == Direction.self: return (False, target_coords)
        if not self.isValidCoordinate(target_coords): return (False, target_coords)
        
        # Get the start and destination index (1D)
        start_idx = self.toIndex(coords)
        target_idx = self.toIndex(target_coords)

        #check if the orgin is valid
        if (
            self.States[start_idx].person is None
            or not self.States[start_idx].person.isZombie
        ):
            return[False, target_idx]
        
        
        # Check if the destination is valid
        if (
            self.States[target_idx].person is None
            or self.States[target_idx].person.isZombie
            or self.States[target_idx].safeSpace
        ):
            return [False, target_idx]
        
        #calculate probability
        chance = 100
        target = self.States[target_idx].person
        if target.isVaccinated:
            chance = 15
        elif target.wasVaccinated != target.wasCured:
            chance = 75
        elif target.wasVaccinated and target.wasCured:
            chance = 50

        # Execute Bite
        r = rd.randint(0, 100)
        if r < chance:
            newTarget = target.clone()
            newTarget.isZombie = True
            newTarget.isVaccinated = False
            self.States[target_idx].person = newTarget
        return [True, target_idx]

    def heal(self, coords: Tuple[int, int], direction: Direction, role: Role) -> Tuple[bool, int]:
        """
        the person at the stated coordinate heals the zombie to the person's stated direction
        If no person is selected, then return [False, None]
        if a person is vaccined, then return [True, index]
        """
        target_coords = self.getTargetCoords(coords, direction)
        if not self.isValidCoordinate(target_coords): return (False, target_coords)
        
        # Get the start and destination index (1D)
        start_idx = self.toIndex(coords)
        target_idx = self.toIndex(target_coords)

        #check if the orgin is valid
        if (
            self.States[start_idx].person is None
            or self.States[start_idx].person.isZombie
            or self.States[start_idx].safeSpace
        ):
            return[False, target_idx]
        
        
        # Check if the destination is valid
        if (
            self.States[target_idx].person is None
        ):
            return [False, target_idx]
            
        #probability of heal vs failed heal
        if self.States[target_idx].person.isZombie:
            chance = 50
        else:
            chance = 100
        
        r = rd.randint(0, 100)
        if r < chance:
            #implement heal
            newTarget = self.States[target_idx].person.clone()
            newTarget.isZombie = False
            newTarget.wasCured = True
            newTarget.isVaccinated = True
            newTarget.turnsVaccinated = 1
            self.States[target_idx].person = newTarget
        else:
            #implement failed heal
            self.bite(target_coords, reverse_dir[direction], role)
        return [True, target_idx]

    def kill(self, coords: Tuple[int, int], direction: Direction, role: Role) -> Tuple[bool, int]:
        target_coords = self.getTargetCoords(coords, direction)
        if direction == Direction.self: return (False, target_coords)
        if not self.isValidCoordinate(target_coords): return (False, target_coords)
        
        # Get the start and destination index (1D)
        start_idx = self.toIndex(coords)
        target_idx = self.toIndex(target_coords)

        #check if the orgin is valid
        if (
            self.States[start_idx].person is None
            or self.States[start_idx].person.isZombie
            or self.States[start_idx].safeSpace
        ):
            return[False, target_idx]
        
        
        # Check if the destination is valid
        if (
            self.States[target_idx].person is None
            or not self.States[target_idx].person.isZombie
        ):
            return [False, target_idx]

        # Execute Kill
        self.States[target_idx].person = None
        return [True, target_idx]

    #gets all the locations of people or zombies on the board (this can be used to count them as well)
    def get_possible_states(self, role_number: int):
        indexes = []
        i = 0
        for state in self.States:
            if state.person != None:
                if role_number == 1 and state.person.isZombie == False:
                    indexes.append(i)
                elif role_number == -1 and state.person.isZombie:
                    indexes.append(i)
            i += 1
        return indexes

    # runs each choice for the qlearning algorithm
    def step(self, role_number: int, learningRate: float):
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

        #make between 7 and boardsize/3 people
        allppl = rd.sample(range(len(self.States)), rd.randint(7, ((self.rows * self.columns) / 3)))
        for state in range(len(self.States)):
            self.States[state].person = None
            if state in allppl:
                self.States[state].person = Person(False)
                self.population += 1
                
        #turn half the humans into zombies
        allzombs = rd.sample(range(len(allppl)), len(allppl)//2)
        for person in range(len(allppl)):
            if person in allzombs:
                self.States[allppl[person]].person.isZombie = True

        #add two safe spaces
        noZombieInSafe = False
        while not noZombieInSafe:
            allsafes = rd.sample(range(len(self.States)), rd.randint(1, (self.rows*self.columns)//15))
            for state in range(len(self.States)):
                if (
                    self.States[state].person is not None
                    and self.States[state].person.isZombie
                ):
                    continue
                else:
                    noZombieInSafe = True

                if state in allsafes:
                    self.States[state].safeSpace = True
