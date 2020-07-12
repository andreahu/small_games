import itertools
import random


class Minesweeper(): #This class has been entirely implemented
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines

class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self): #AH implemented
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        if self.count == 0:
            return None
        elif len(self.cells) == self.count:
            return self.cells
        else:
            return None
        

    def known_safes(self): #AH implemented
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count == 0:
            return self.cells
        else:
            return None


    def mark_mine(self, cell): #AH implemented
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            self.cells.remove(cell)
            # Can count be zero?
            if self.count >= 0:
                # raise Exception("wrong logic! sentence already zero")
                self.count -= 1

    def mark_safe(self, cell): #AH implemented
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:
            self.cells.remove(cell)


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count): #AH implemented
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.
        """

        """1) mark the cell as a move that has been made"""
        self.moves_made.add(cell)

        """2) mark the cell as safe"""
        self.safes.add(cell)

        """3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
        """

        newCells = set()

        i = cell[0]
        j = cell[1]

        # add all the neighbor cells into the newCells set
        for x in (-1, 0, 1):
            for y in (-1, 0, 1):
                if x!= 0 or y != 0:
                    newI = i + x
                    newJ = j + y
                    if newI in range(self.height) and newJ in range(self.width):
                        if (newI, newJ) in self.safes:
                            continue
                        elif (newI, newJ) in self.mines:
                            count -= 1
                        else:
                            newCells.add((newI, newJ))

        #create a new sentence and add to knowledge
        if len(newCells) > 0:
            newSentence = Sentence(newCells, count) 
            self.knowledge.append(newSentence)

        """4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base"""
        self.updateKnowledge()

        """5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge"""
        newKnowledge = []

        #look for the overlapped sentences in the knowledge
        for sentence_1 in self.knowledge:
            for sentence_2 in self.knowledge:
                if sentence_1 != sentence_2 and sentence_1.cells.issubset(sentence_2.cells):
                    count = sentence_2.count - sentence_1.count
                    if count >= 0:
                        newCells = sentence_2.cells.difference(sentence_1.cells)
                        if len(newCells) == 0:
                            break
                        newSentence = Sentence(newCells, count) 
                        # Only keep knowledge that we don't know before.
                        if newSentence not in self.knowledge and newSentence not in newKnowledge:
                            newKnowledge.append(newSentence)
        
        self.knowledge.extend(newKnowledge)
        self.updateKnowledge()


    def make_safe_move(self): #AH implemented
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        if len(self.safes) != 0:
            for move in self.safes:
                if move not in self.moves_made:
                    return move
        return None


    def make_random_move(self): #AH implemented
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        
        movesToMake = set()

        for i in range(self.height):
            for j in range(self.width):
                if ((i,j) not in self.mines) and ((i,j) not in self.moves_made):
                    movesToMake.add((i,j)) 
        
        if len(movesToMake) > 0:
            return random.choice(list(movesToMake))
        else:
            return None

    def done(self):
        """
            Returns True if the game is done.
        """
        if len(self.safes) + len(self.mines) == self.height * self.width:
            print("+++++++++++++++")
            print("DONE!!!!")
            print(self.mines)
            return True
        return False

    def updateKnowledge(self):
        """
            Updates the knowledge based on existing knowledge, until no new knowledge is generated.
        """
        dirty = True

        while(dirty):
            dirty = False
            mines = set()
            safes = set()
            for s in self.knowledge:
                known_mines = s.known_mines()
                if known_mines is not None:
                    newMines = known_mines.difference(self.mines)
                    mines.update(newMines)
                known_safes = s.known_safes()
                if known_safes is not None:
                    newSafes = known_safes.difference(self.safes)
                    safes.update(newSafes)
            
            for m in mines:
                self.mark_mine(m)
                dirty = True
            for s in safes:
                self.mark_safe(s)
                dirty = True

            # Remove empty sentences
            EMPTY_SENTENCE = Sentence(set(), 0)
            self.knowledge = list(filter((EMPTY_SENTENCE).__ne__, self.knowledge))

            if self.done():
                break