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
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
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
            for word in self.domains[
                var
            ].copy():  # copy() to fix "Set changed size during iteration" error
                if len(word) != var.length:
                    self.domains[var].remove(word)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        revised = False
        for x_word in self.domains[x].copy():
            hasCorresponding = False
            for y_word in self.domains[y]:
                # Check if x and y overlap
                overlap = self.crossword.overlaps[x, y]
                if overlap is None:
                    continue
                i, j = overlap
                # Check if the character at the overlap match
                if x_word[i] == y_word[j]:
                    hasCorresponding = True
                    break
            if not hasCorresponding:
                self.domains[x].remove(x_word)
                revised = True
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
            for x in self.domains:
                for y in self.domains:
                    if x != y and self.crossword.overlaps[x, y] is not None:
                        arcs.append((x, y))
        while arcs:
            (x, y) = arcs.pop()  # Get an arc (x, y) from the list for processing
            if self.revise(x, y):  # If a revision was made
                if not self.domains[x]:  # If domain is empty
                    return False
                for z in self.domains:
                    if z != x and z != y and self.crossword.overlaps[x, z] is not None:
                        arcs.append(
                            (z, x)
                        )  # Add (z, x) to the list of arcs to be processed
        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        # Check the length
        if len(assignment) != len(self.crossword.variables):
            return False
        # Check each variable is assigned a value of correct length
        for var in self.crossword.variables:
            if var not in assignment:
                return False
            if assignment[var] is None:
                return False
            if len(assignment[var]) != var.length:
                return False
        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        # This does not require assignment to be complete

        # All values must be distinct
        if len(set(assignment.values())) != len(assignment):
            return False

        # Every value is of the correct length
        for var, word in assignment.items():
            if len(word) != var.length:
                return False

        # For each pair of variables with an overlap
        # `self.crossword.overlaps` is a dictionary. Keys are (x, y) tuples, values are (i, j) or None.
        for (x, y), overlap in self.crossword.overlaps.items():
            if overlap is None:
                continue
            if x in assignment and y in assignment:
                i, j = overlap
                if assignment[x][i] != assignment[y][j]:
                    return False

        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        def count_rule_outs(value):
            count = 0
            for neighbor in self.crossword.neighbors(var):
                if neighbor in assignment:
                    continue  # Skip assigned neighbors
                i, j = self.crossword.overlaps[var, neighbor]

                # For each word in the neighbor's domain, check if it conflicts with this value
                for word in self.domains[neighbor]:
                    if value[i] != word[j]:
                        count += 1  # If the overlap characters don't match, then this value is ruled out for the neighbor

            return count

        return sorted(self.domains[var], key=count_rule_outs)

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        # Function to find the number of remaining values in the domain
        def domain_size(var):
            return len(self.domains[var])

        # Function to find the degree of the variable
        def degree(var):
            return len(self.crossword.neighbors(var))

        # Select the unassigned variable with the minimum domain size and then the highest degree
        unassigned = [v for v in self.domains if v not in assignment]
        if not unassigned:
            return None  # Return None if all variables are assigned
        return min(unassigned, key=lambda v: (domain_size(v), -degree(v)))

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        # If assignment is complete, return it
        if self.assignment_complete(assignment):
            return assignment

        # Select an unassigned variable
        var = self.select_unassigned_variable(assignment)

        for value in self.order_domain_values(var, assignment):
            new_assignment = assignment.copy()
            new_assignment[var] = value
            # If the assignment is consistent, call backtrack
            if self.consistent(new_assignment):
                result = self.backtrack(new_assignment)
                if result is not None:
                    return result
        return None  # If no solution, return None


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
