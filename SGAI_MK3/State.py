from Person import Person

class State:
    def __init__(self, p: Person, i, safeSpace = False) -> None:
        self.person = p
        self.location = i
        self.safeSpace = safeSpace
        pass

    def distance(self, other_id): # gets the distance between two states
        first_coord = self.toCoord(self.location)
        second_coord = self.toCoord(other_id)
        return (float)((second_coord[1] - first_coord[1])**2 + (second_coord[0] - first_coord[0])**2)**0.5

    def nearest_zombie(self, GameBoard):  #pretty self explanatory
        smallest_dist = 100
        for state in GameBoard.States:
            if state.person != None:
                if state.person.isZombie:
                    d = self.distance(GameBoard, state.location)
                    if d < smallest_dist:
                        smallest_dist = d
        return smallest_dist

    def evaluate(self, action: str, GameBoard): # decides on the reward for a specific action based on what the board is like (for q learning)
        reward = 0
        reward += self.nearest_zombie(GameBoard) - 3
        if action == "heal":
            reward += 5
        elif action == "bite" and self.person.isZombie:
            chance = 0
            if self.person.wasVaccinated != self.person.wasCured:
                chance = 0.25
            if self.person.wasVaccinated and self.person.wasCured:
                chance = 0.5
            reward = reward + int(5 * (2 + chance))
        return reward

    def adjacent(self, GameBoard):  # returns the four adjacent boxes that are in bounds
        newCoord = GameBoard.toCoord(self.location)
        print(newCoord)
        moves = [              #puts all four adjacent locations into moves
            (newCoord[0], newCoord[1] - 1),
            (newCoord[0], newCoord[1] + 1),
            (newCoord[0] - 1, newCoord[1]),
            (newCoord[0] + 1, newCoord[1]),
        ]
        remove = []  #creates the ones to remove
        for i in range(4):
            move = moves[i]
            if (        #removes all illigal options
                move[0] < 0
                or move[0] > GameBoard.columns
                or move[1] < 0
                or move[1] > GameBoard.rows
            ):
                remove.append(i)
        remove.reverse()
        for r in remove:
            moves.pop(r)
        return moves

    def clone(self): #clones the state (for the purpose of moving people and zombies)
        if self.person is None:
            return State(self.person, self.location)
        return State(self.person.clone(), self.location)

    def __eq__(self, __o: object) -> bool: # compares if two states are the same, not just the same person but also the same location
        if type(__o) == State:
            return self.person == __o.person and self.location == __o.location
        return False

    def __ne__(self, __o: object) -> bool: # same as over but not equals
        return not self == __o
