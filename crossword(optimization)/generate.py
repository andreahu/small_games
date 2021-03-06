import sys
import math 
from operator import itemgetter, attrgetter 

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())


    def enforce_node_consistency(self): 
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        # domains property: a dictionary that maps variables to a set of possible words the variable might take on as a value
        for var in self.domains:
            removed = []
            for word in self.domains[var]:
                if len(word) != var.length:
                    removed.append(word)
            for r in removed:
                self.domains[var].remove(r)
                    

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
       
        revised = False
        overlap = self.crossword.overlaps[x,y]

        if overlap != None:
            i = overlap[0]
            j = overlap[1]
            removed = []
            for xWord in self.domains[x]:
                match = False
                letter = xWord[i]
                for yWord in self.domains[y]:
                    if yWord[j] == letter:
                        match = True
                if match == False:
                    removed.append(xWord)
                    revised = True
            for r in removed:
                self.domains[x].remove(r)
        return revised


    def ac3(self, arcs=None): 
        
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """

        if arcs is None:
            arcs = []
            allVariables = self.domains.keys()
            for x in allVariables:
                for y in allVariables:
                    if x is not y and self.crossword.overlaps[x,y] != None:
                        arcs.append((x,y))
        
        while len(arcs) != 0:
            arc = arcs.pop()
            x = arc[0]
            y = arc[1]
            if self.revise(x, y):
                if len(self.domains[x]) == 0:
                    return False
                else:
                    x_neighbors = self.crossword.neighbors(x)
                    for z in x_neighbors:
                        if z != y:
                            arcs.insert(0, (z, x))
        return True
                    

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """

        if len(assignment) == len(self.domains):
            return True
        else:
            return False
            

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """

        valueSet = set()
        for var in assignment:
            value = assignment[var]
            #check uniqueness
            if value in valueSet: 
                return False
            else:
                valueSet.add(value)
            
            #check length
            if len(value) != var.length:
                return False

            # Check conflict
            for anotherVar in assignment:
                if anotherVar is not var:
                    overlap = self.crossword.overlaps[var, anotherVar]
                    if overlap != None:
                        i = overlap[0]
                        j = overlap[1]
                        if assignment[var][i] != assignment[anotherVar][j]:
                            return False
        
        return True
                            



    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """

        valueTupleList = []
        var_neighbors = neighbors(self.crossword, var) 

        for varValue in self.domains[var]:
            count = 0
            for n in var_neighbors:
                if n in assignment.key():
                    continue

                overlap = self.crossword.overlaps(var, n)
                i = overlap[0]
                j = overlap[1]
                targetLetter = varValue[i]
                for nValue in self.domains[n]:
                    if nValue[j] != targetLetter:
                        count += 1

            valueTupleList.append((varValue, count))

        return sorted(valueTupleList, key=itemgetter(1))


    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        allVars = self.domains.keys()
        varsInAssignment = assignment.keys()

        resultVar = None 
        fewest = math.inf
        for var in allVars:
            if var not in varsInAssignment:
                if len(self.domains[var]) < fewest:
                    fewest = len(self.domains[var])
                    resultVar = var
        return resultVar




    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            return assignment

        var = self.select_unassigned_variable(assignment)

        for value in self.domains[var]:
            assignment[var] = value
            if self.consistent(assignment):
                assignment[var] = value
                result = self.backtrack(assignment)
                if result is not None:
                    return result
            assignment.pop(var)
        
        return None

        


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)




if __name__ == "__main__":
    main()
