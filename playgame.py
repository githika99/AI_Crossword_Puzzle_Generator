import random
from hint_generator import get_crossword_hints

class PlayableCrossword:
    def __init__(self, crossword_grid, vocabulary, theme, difficulty):
        """
        Initializes the crossword game.
        :param crossword_grid: A list of lists representing the crossword grid.
        :param vocabulary: A list of words used in the crossword.
        """
        self.grid = crossword_grid
        self.vocabulary = {word: hint for word, hint in get_crossword_hints(theme, vocabulary, difficulty).items()}  # Convert vocabulary to dict
        self.user_answers = {}  
        self.word_positions = self.find_word_positions()

    def find_word_positions(self):
        """Finds positions of both horizontal (Across) and vertical (Down) words in the grid."""
        positions = []
        grid_height = len(self.grid)
        grid_width = len(self.grid[0])

        for word in self.vocabulary.keys(): 
            word = word.lower()

            # Search for words across (horizontal)
            for row in range(grid_height):
                for col in range(grid_width - len(word) + 1):
                    if all(self.grid[row][col + i] in (word[i], '/') for i in range(len(word))):
                        positions.append((word, row, col, 'Across'))

            # Search for words down (vertical)
            for col in range(grid_width):
                for row in range(grid_height - len(word) + 1):
                    if all(self.grid[row + i][col] in (word[i], '/') for i in range(len(word))):
                        positions.append((word, row, col, 'Down'))

        return positions

    def print_grid(self):
        """Displays the crossword grid with empty boxes for unfilled words."""
        print("\n    ", end="")
        for col in range(len(self.grid[0])):
            print(f"{col:2} ", end="") 
        print("\n  +" + "-" * (len(self.grid[0]) * 3 - 1) + "+")

        for row in range(len(self.grid)):
            print(f"{row:2} |", end="") 
            for col in range(len(self.grid[0])):
                char = self.grid[row][col]
                
                # If the letter belongs to a correctly guessed word, show it
                if any(word in self.user_answers and 
                       ((direction == 'Across' and col in range(start_col, start_col + len(word)) and row == start_row) or
                        (direction == 'Down' and row in range(start_row, start_row + len(word)) and col == start_col))
                       for word, start_row, start_col, direction in self.word_positions):
                    print(f" {char} ", end="")  
                
                # If it's part of an unsolved word, show an empty box
                elif char.isalpha():
                    print(" □ ", end="")  

                # Otherwise, it's just an empty space
                else:
                    print(" . ", end="")  

            print("|")

        print("  +" + "-" * (len(self.grid[0]) * 3 - 1) + "+\n")

    def play(self):
        """Main game loop where the user attempts to solve the crossword."""
        print("Welcome to the Crossword Puzzle Game!")
        print("Fill in the words based on the provided hints.\n")

        while len(self.user_answers) < len(self.vocabulary):
            self.print_grid()
            print("Hints:")
            for i, (word, row, col, direction) in enumerate(self.word_positions):
                if word not in self.user_answers:
                    hint_text = self.vocabulary.get(word, "Unknown hint") 
                    print(f"{i + 1}. ({direction} at row {row}, col {col}): {hint_text} ({len(word)} letters)") 

            try:
                choice = int(input("\nEnter the number of the word you want to solve: ")) - 1
                if choice < 0 or choice >= len(self.word_positions):
                    print("Invalid choice, try again.")
                    continue
            except ValueError:
                print("Please enter a valid number.")
                continue

            word, row, col, direction = self.word_positions[choice]
            guess = input(f"Enter your guess for '{self.vocabulary[word]}' ({direction} at row {row}, col {col}): ").strip().lower()

            if guess == word:
                print("Correct!\n")
                self.user_answers[word] = word  
            else:
                print("Incorrect. Try again!\n")

        print("\nCongratulations! You've solved the crossword puzzle! 🎉")
        self.print_grid()
