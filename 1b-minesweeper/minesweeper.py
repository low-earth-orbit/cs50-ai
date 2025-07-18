import itertools
import random


class Minesweeper:
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


class Sentence:
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

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        if len(self.cells) == self.count and self.count != 0:
            return self.cells
        return set()  # return empty cells if unknown

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count == 0:
            return self.cells
        return set()

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1  # decrement count - mine is removed

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:
            self.cells.remove(cell)


class MinesweeperAI:
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

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        # 1. Mark the cell as a move that has been made
        self.moves_made.add(cell)
        # 2. Mark the cell as safe
        self.mark_safe(cell)

        # 3. Add a new sentence to the AI's knowledge base
        neighbours = set()
        number_known_mines = 0
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):
                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    neighbour = (i, j)
                    if neighbour in self.mines:
                        number_known_mines += 1  # neighbour is a known mine
                    elif neighbour not in self.safes:
                        neighbours.add(
                            neighbour
                        )  # only neighbours that are not known are added
        adjusted_count = count - number_known_mines
        if neighbours:
            if adjusted_count == 0:
                for neighbour in neighbours:
                    self.mark_safe(neighbour)
            elif adjusted_count == len(neighbours):
                for neighbour in neighbours:
                    self.mark_mine(neighbour)
            else:
                new_sentence = Sentence(neighbours, adjusted_count)  # The new sentence
                if (
                    new_sentence not in self.knowledge and new_sentence.cells
                ):  # Only add if not redundant
                    self.knowledge.append(new_sentence)

        # 4. Mark new safes/mines
        self.infer()

        # 5. Infer new sentences from existing ones
        while True:
            new_sentences = []
            for s1 in self.knowledge:
                for s2 in self.knowledge:
                    if s1 == s2 or not s1.cells or not s2.cells:
                        continue
                    if s1.cells < s2.cells:
                        diff_cells = s2.cells - s1.cells
                        diff_count = s2.count - s1.count
                        if diff_cells:
                            new_sentence = Sentence(diff_cells, diff_count)
                            if (
                                new_sentence not in self.knowledge
                                and new_sentence not in new_sentences
                            ):
                                new_sentences.append(new_sentence)
            if not new_sentences:
                break
            self.knowledge.extend(new_sentences)
            self.infer()
        # Remove empty sentences
        self.knowledge = [s for s in self.knowledge if s.cells]

    def infer(self):
        """
        Perform inference based on current knowledge:
        repeatedly mark new safe cells and mine cells
        """
        while True:
            inference_made = False
            for sentence in self.knowledge:
                if not sentence.cells:
                    continue
                sentence_mines = list(sentence.known_mines())
                sentence_safes = list(sentence.known_safes())
                for mine in sentence_mines:
                    if mine not in self.mines:
                        self.mark_mine(mine)
                        inference_made = True
                for safe in sentence_safes:
                    if safe not in self.safes:
                        self.mark_safe(safe)
                        inference_made = True
            if not inference_made:
                break

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        for move in self.safes:
            if move not in self.moves_made:
                return move
        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        choices = [
            (i, j)
            for i in range(self.height)
            for j in range(self.width)
            if (i, j) not in self.mines and (i, j) not in self.moves_made
        ]
        if choices:
            return random.choice(choices)
        return None
