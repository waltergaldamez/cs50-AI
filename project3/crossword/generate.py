import sys

from collections import deque

from crossword import Crossword, Variable


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
        for var in self.domains:
            copy = self.domains[var].copy()
            for value in copy:
                if len(value) != var.length:
                    self.domains[var].remove(value)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        intersection = self.crossword.overlaps[x, y]
        if intersection is None:
            return False
        
        change = False
        x_words = self.domains[x].copy()
        y_words = self.domains[y].copy()

        for x_word in x_words:
            found = False
            for y_word in y_words:
                if x_word[intersection[0]] == y_word[intersection[1]]:
                    found = True
                    break
            if not found:
                self.domains[x].remove(x_word)
                change = True

        return change

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
            for var in self.domains:
                for var_2 in self.domains:
                    if var == var_2:
                        continue
                    elif self.crossword.overlaps[var, var_2] is not None:
                        arcs.append((var, var_2))
        while len(arcs) != 0:
            (x, y) = arcs.pop(0)
            if self.revise(x, y):
                if len(self.domains[x]) == 0:
                    return False
                for var in self.domains:
                    if var == x:
                        continue
                    elif self.crossword.overlaps[x, var] is not None:
                        arcs.append((x, var))
        
        return True


    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        for var in self.domains:
            if var not in assignment or assignment[var] is None:
                return False
        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        words = set()

        for variable in assignment:
            if assignment[variable] in words:
                return False
            else:
                words.add(assignment[variable])
            
            if len(assignment[variable]) != variable.length:
                return False
            
            neighbors = self.crossword.neighbors(variable)

            for neighbor in neighbors:
                intersection = self.crossword.overlaps[variable, neighbor]
                if intersection is not None:
                    if neighbor in assignment:
                        if assignment[variable][intersection[0]] is not assignment[neighbor][intersection[1]]:
                            return False
        return True


    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        mapping = dict()
        neighbors = self.crossword.neighbors(var)

        for word in self.domains[var]:
            count = 0
            for neighbor in neighbors:
                if neighbor not in assignment:
                    if word in self.domains[neighbor]:
                        count += 1
            if mapping[count] is None:
                mapping[count] = set()
            mapping[count].add(word)
        
        ret_list = []

        for count in sorted(mapping.keys()):
            for word in mapping[count]:
                ret_list.add(word)
        
        return ret_list

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        mappings = dict()
        for var in self.domains:
            if var not in assignment:
                if len(self.domains[var]) not in mappings:
                    mappings[len(self.domains[var])] = set()
                mappings[len(self.domains[var])].add(var)
        
        least = sorted(mappings.keys())[0]

        if len(mappings[least]) == 1:
            for item in mappings[least]:
                return item
        else:
            highest = None
            for item in mappings[least]:
                if highest is None or len(self.crossword.neighbors(highest)) < len(self.crossword.neighbors(item)):
                    highest = item
            return highest

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
                result = self.backtrack(assignment)
                if result is not None:
                    return result
            assignment.pop(var, None)
        
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
