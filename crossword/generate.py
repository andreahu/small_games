import sys

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
        for variable in self.domains:
            for word in self.domains[variable]:
                if len(word) != variable.length
                self.domains[variable].remove(word) #ah: modified the set while iterating. cast the set to a list?

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        #AH: below are the preudo code in class.  
        # function REVISE(csp, X, Y):
        #     revised = false
        #     for x in X.domain:
        #         if no y in Y.domain satisfies constraint for (X, Y):
        #             delete x from X.domain
        #             revised = true
        #     return revised
       
        revised = False
        overlap = self.crossword.overlaps[x,y]

        if overlap != None:
            i = overlap[0]
            j = overlap[1]
            for xWord in self.domains[x]:
                match = False
                letter = xWord[i]
                for yWord in self.domains[y]:
                    if yWord[j] == letter:
                        match = True
                if match == False:
                    self.domains[x].remove[xWord] #ah: modified the set while iterating. cast the set to a list?
                    revised = True
        return revised


    def ac3(self, arcs=None): 
        #ah:if need to change a set while iterating it, you could cast it into a list
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        #AH: below are the preudo code in class. https://cdn.cs50.net/ai/2020/spring/lectures/3/lecture3.pdf
    #   function AC-3(csp):
    #     queue = all arcs in csp
    #     while queue non-empty:
    #         (X, Y) = DEQUEUE(queue)
    #         if REVISE(csp, X, Y):
    #             if size of X.domain == 0:
    #                 return false
    #             for each Z in X.neighbors - {Y}:
    #                 ENQUEUE(queue, (Z, X))
    #     return true

        allVariables = self.domains.keys()
        for x in allVariables:
            for y in allVariables:
                if x is not y and self.crossword.overlaps[x,y] != None:
                    if (y,x) not in arcs: # should I set this to avoid duplication?
                        arcs.append((x,y))
        
        while len(arcs) != 0:
            arc = arcs[len(arcs)-1]
            arcs.pop()
            x = arc[0]
            y = arc[1]
            if revise(self, x, y):
                if len(self.domains[x]) == 0:
                    return False
                else:
                    x_neighbors = neighbors(self.crossword, x)
                    for z in x_neighbors:
                        if z != y:
                            arcs.append((z, x))
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

        varSet = set()

        for var in assignment:
            if var in varSet: #check uniqueness
                return False

            for word in assignment[var]: #check length
                if len(word) != var.length:
                    return False

            var_neighbors = neighbors(self.crossword, var)
            


                    
        











    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        
        










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
        fewest = 9999
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

        #ah: below is preudo code in class.  https://cdn.cs50.net/ai/2020/spring/lectures/3/lecture3.pdf
        """
        function BACKTRACK(assignment, csp):
            if assignment complete: return assignment
            var = SELECT-UNASSIGNED-VAR(assignment, csp)
            for value in DOMAIN-VALUES(var, assignment, csp):
                if value consistent with assignment:
                    add {var = value} to assignment
                    result = BACKTRACK(assignment, csp)
                    if result ≠ failure: return result
                remove {var = value} from assignment
            return failure
        """
        #ah: improved the code above for maintaining arc-consistency. In this case, could add a helper function
        """
        function BACKTRACK(assignment, csp):
            if assignment complete: return assignment
            var = SELECT-UNASSIGNED-VAR(assignment, csp)
            for value in DOMAIN-VALUES(var, assignment, csp):
            if value consistent with assignment:
                add {var = value} to assignment
                inferences = INFERENCE(assignment, csp)
                if inferences ≠ failure: add inferences to assignment
                result = BACKTRACK(assignment, csp)
                if result ≠ failure: return result
                remove {var = value} and inferences from assignment
            return failure

        """






        raise NotImplementedError


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



    #ah test
    # print(crossword.words)


if __name__ == "__main__":
    main()
