import imp
from tracemalloc import start
from State import State
import random as rd
from Person import Person
from typing import List, Tuple
from Enums import *


class Board:
    def __init__(
        self,
        dimensions: Tuple[int, int],
        border: int,
        cell_dimensions: Tuple[int, int],
        player_role: str,
    ):
        self.rows = dimensions[0]
        self.columns = dimensions[1]
        self.display_border = border
        self.display_cell_dimensions = cell_dimensions
        self.Player_Role = player_role
        self.population = 0
        self.States = []
        self.QTable = []
        for s in range(dimensions[0] * dimensions[1]):
            self.States.append(State(None, s))
            self.QTable.append([0] * 6)

        self.actionToFunction = {
            Action.move: self.move,
            Action.heal: self.heal,
            Action.bite: self.bite,
        }

    def num_zombies(self) -> int:
        r = 0
        for state in self.States:
            if state.person != None:
                if state.person.isZombie:
                    r += 1
        return r

    def containsPerson(self, isZombie: bool):
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
                        and B.actionToFunction[action](B.toCoord(state.location), direction)[0]
                    ):
                        poss.append(B.toCoord(state.location))
                        changed_states = True

                    if changed_states:
                        # reset the states
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
                if state.person is not None:
                    changed_states = False
                    if (
                        not state.person.isZombie
                        and B.actionToFunction[action](B.toCoord(state.location), direction)[0]
                    ):
                        poss.append(B.toCoord(state.location))
                        changed_states = True

                    if changed_states:
                        # reset the states
                        B.States = [
                            self.States[i].clone()
                            if self.States[i] != B.States[i]
                            else B.States[i]
                            for i in range(len(self.States))
                        ]
        return poss

    def toCoord(self, i: int):
        return (int(i % self.columns), int(i / self.rows))

    def toIndex(self, coordinates: Tuple[int, int]):
        return int(coordinates[1] * self.columns) + int(coordinates[0])

    def isValidCoordinate(self, coordinates: Tuple[int, int]):
        return (
            coordinates[1] < self.rows
            and coordinates[1] >= 0
            and coordinates[0] < self.columns
            and coordinates[0] >= 0
        )

    def clone(self, L: List[State], role: str):
        NB = Board(
            (self.rows, self.columns),
            self.display_border,
            self.display_cell_dimensions,
            self.Player_Role,
        )
        NB.States = [state.clone() for state in L]
        NB.Player_Role = role
        return NB

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
        
        return new_coords
    
    def move(self, coords: Tuple[int, int], direction: Direction) -> Tuple[bool, int]:    
        new_coords = self.getTargetCoords(coords, direction)
        
        # Get the start and destination index (1D)
        start_idx = self.toIndex(coords)
        destination_idx = self.toIndex(new_coords)

        # Check if the new coordinates are valid
        if not self.isValidCoordinate(new_coords):
            return [False, destination_idx]

        # Check if the destination is currently occupied
        if self.States[destination_idx].person is None:
            #Execute Move
            self.States[destination_idx].person = self.States[start_idx].person
            self.States[start_idx].person = None
            return [True, destination_idx]
        return [False, destination_idx]

    def QGreedyat(self, state_id):
        biggest = self.QTable[state_id][0] * self.Player_Role
        ind = 0
        A = self.QTable[state_id]
        i = 0
        for qval in A:
            if (qval * self.Player_Role) > biggest:
                biggest = qval
                ind = i
            i += 1
        return [ind, self.QTable[ind]]  # action_index, qvalue

    def choose_action(self, state_id: int, lr: float):
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

    def bite(self, coords: Tuple[int, int], direction: Direction) -> Tuple[bool, int]:
        target_coords = self.getTargetCoords(coords, direction)
        
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
        ):
            return [False, target_idx]
        
        #calculate probability
        chance = 100
        target = self.States[target_idx].person
        if target.isVaccinated:
            chance = 20
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

    def heal(self, coords: Tuple[int, int], direction: Direction) -> Tuple[bool, int]:
        """
        the person at the stated coordinate heals the zombie to the person's stated direction
        If no person is selected, then return [False, None]
        if a person is vaccined, then return [True, index]
        """
        target_coords = self.getTargetCoords(coords, direction)
        
        # Get the start and destination index (1D)
        start_idx = self.toIndex(coords)
        target_idx = self.toIndex(target_coords)

        #check if the orgin is valid
        if (
            self.States[start_idx].person is None
            or self.States[start_idx].person.isZombie
        ):
            return[False, target_idx]
        
        
        # Check if the destination is valid
        if (
            self.States[target_idx].person is None
            or not self.States[target_idx].person.isZombie
        ):
            return [False, target_idx]
            
        #probability of heal vs failed heal
        chance = 50
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
            self.bite(target_coords, reverse_dir[direction])
        return [True, target_idx]

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

    def step(self, role_number: int, learningRate: float):
        P = self.get_possible_states(role_number)
        r = rd.uniform(0, 1)
        if r < learningRate:
            rs = rd.randrange(0, len(self.States) - 1)
            if role_number == 1:
                while (
                    self.States[rs].person is not None
                    and self.States[rs].person.isZombie
                ):
                    rs = rd.randrange(0, len(self.States) - 1)
            else:
                while (
                    self.States[rs].person is not None
                    and self.States[rs].person.isZombie == False
                ):
                    rs = rd.randrange(0, len(self.States) - 1)

            # random state and value
        # old_value = QTable[state][acti]
        # next_max = np.max(QTable[next_state])
        # new_value = (1 - alpha) * old_value + alpha * (reward + gamma * next_max)
        # QTable[state][acti] = new_value

    def populate(self):
        total = rd.randint(7, ((self.rows * self.columns) / 3))
        poss = []
        for x in range(len(self.States)):
            r = rd.randint(0, 100)
            if r < 60 and self.population < total:
                p = Person(False)
                self.States[x].person = p
                self.population = self.population + 1
                poss.append(x)
            else:
                self.States[x].person = None
        used = []
        for x in range(4):
            s = rd.randint(0, len(poss) - 1)
            while s in used:
                s = rd.randint(0, len(poss) - 1)
            self.States[poss[s]].person.isZombie = True
            used.append(s)
