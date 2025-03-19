import copy
import multiprocessing.pool as mpool
import random

# the object of each word
class Word():
    def __init__(self, w ,startPos = (0,0), len = 0,isHorizontal = True):
        self._word = w;                 #word
        self._startPos =startPos        #start pos(tutle)
        self._length = len;             #len
        self._isHorizontal = isHorizontal ##if false Word is vertical

    def getPos(self):
        return self._startPos;

    def get_length(self):
        return self._length;

    def getWord(self):
        return self._word
    
    def isHorizontal(self):
        return self._isHorizontal;

    def reset(self,startPos , len ,isHorizontal ):
        self._startPos =startPos
        self._length = len;
        self._isHorizontal = isHorizontal


class Individual():
    #Parameters vocabulary_list : list A list of words to be placed in the crossword grid.
    def __init__(self, vocabulary_list):

        self._vocabulary_list = []
        for word in vocabulary_list:
            if(word[0] != '/'):
                self._vocabulary_list.append('/'+word+'/');
            else:
                self._vocabulary_list.append(word);
        
        #self._vocabulary_list = vocabulary_list

        self._vocabulary_record = {}; #dictonary for each word (key: word item:Word object)
        self.fitness = 0;
        self.group_penalty =0; #debug used to check the penalty of each group

        self._grid_width, self._grid_height = self.calculate_grid_size()
        self._cross_word_grid = self.generate_individual_intersect(self._vocabulary_list)
        self.calculate_fitness();
    


    def __lt__(self, other):
        # For a max-heap using heapq (which is a min-heap), 
        # we invert the comparison so higher fitness comes first
        return self.getFitness() > other.getFitness()
    
    
    def __gt__(self, other):
        return self.getFitness() < other.getFitness()
    
    def __eq__(self, other):
        return self.getFitness() == other.getFitness()
    
    def get_height(self):
        return self._grid_height;
    def get_width(self):
        return self._grid_width;
    def getFitness(self):
        return self.fitness;





    #Calculate an appropriate grid size based on the vocabulary list.
    #Returns:  A tuple containing (width, height) of the grid.
    def calculate_grid_size(self):
        if not self._vocabulary_list:
            return (10, 10)  # Default size for empty vocabulary
        
        # Find the longest word
        max_word_length = max(len(word) for word in self._vocabulary_list)
        
        
        total_chars = sum(len(word) for word in self._vocabulary_list)
        
        # Calculate a base size that would fit all words if they were laid out
        # with no overlapping (adding some extra space)
        base_size = int(total_chars ** 0.5) + 2
        
        # Ensure the grid is at least as large as the longest word plus some buffer
        min_dimension = max_word_length + 4
        
        
        width = max(base_size, min_dimension)
        height = max(base_size, min_dimension)
        
        # For larger vocabularies, add even more space
        if len(self._vocabulary_list) > 10:
            width += 5
            height += 5
        
        
        width += random.randint(0, 5)
        height += random.randint(0, 5)
        
        return (width, height)
    




    #Generate a crossword grid with words placed randomly. (Not recommand);
    #Returns:  A 2D array representing the crossword grid.
    # Parameters: vocabulary_list :   A list of words to be placed in the crossword grid.
    def generate_individual_random(self, vocabulary_list):
        # Initialize grid with '.' characters
        grid = [['.' for _ in range(self._grid_width)] for _ in range(self._grid_height)]
        self._cross_word_grid = grid
        
        # Sort words by length (longest first) to optimize placement
        sorted_words = sorted(vocabulary_list, key=len, reverse=True)
        
        for word_str in sorted_words:
            placed = False
            max_attempts = 100
            
            for _ in range(max_attempts):
                # Randomly choose orientation (0 for horizontal, 1 for vertical)
                is_horizontal = random.choice([True, False])
                
                if is_horizontal:
                    row = random.randint(0, self._grid_height - 1)
                    col = random.randint(0, self._grid_width - len(word_str))
                else:  # Vertical
                    row = random.randint(0, self._grid_height - len(word_str))
                    col = random.randint(0, self._grid_width - 1)
                
                
                word_obj = Word(word_str, startPos=(row, col), len=len(word_str), isHorizontal=is_horizontal)
                
                
                if self.place_word(word_obj):
                    placed = True
                    break
            
            if not placed:
                #if not place the word print warning.
                print(f"Warning: Could not place word '{word_str}' in the grid")
        
        return self._cross_word_grid
    


    #Generate a crossword grid with words placed strategically to maximize intersections. Words are placed to intersect with existing words whenever possible.(Recommand)
    #Parameters:vocabulary_list : list  A list of words to be placed in the crossword grid.
    # list of lists   A 2D array representing the crossword grid.
    def generate_individual_intersect(self, vocabulary_list):

        # Initialize grid with ' ' characters
        grid = [[' ' for _ in range(self._grid_width)] for _ in range(self._grid_height)]
        self._cross_word_grid = grid
        
        # Sort words by length (longest first) to optimize placement
        sorted_words = sorted(vocabulary_list, key=len, reverse=True)
        
        # Place the first word in the center of the grid
        if sorted_words:
            first_word = sorted_words[0]
            center_row = self._grid_height // 2
            center_col = max(0, (self._grid_width - len(first_word)) // 2)
            
            # Try horizontal first, then vertical if horizontal fails
            first_word_obj = Word(first_word, startPos=(center_row, center_col), 
                                len=len(first_word), isHorizontal=True)
            
            if not self.place_word(first_word_obj):
                # Try vertical placement
                center_col = self._grid_width // 2
                center_row = max(0, (self._grid_height - len(first_word)) // 2)
                first_word_obj = Word(first_word, startPos=(center_row, center_col), 
                                    len=len(first_word), isHorizontal=False)
                
                if not self.place_word(first_word_obj):
                    # If both fail, try random positions
                    self._place_word_randomly(first_word)
        



        # Place remaining words
        for word_str in sorted_words[1:]:
            placed = self._place_word_with_intersection(word_str)
            
            if not placed:
                # If intersection placement fails, try random placement
                placed = self._place_word_randomly(word_str)
                if not placed:
                    print(f"Warning: Could not place word '{word_str}' in the grid")
        
        return self._cross_word_grid
    




    #Try to place a word so that it intersects with existing words.
    #word_str : str The word to place.
    #Returns:True if the word was successfully placed, False otherwise.
    def _place_word_with_intersection(self, word_str):

        # If no words are placed yet, place randomly
        if not self._vocabulary_record:
            return self._place_word_randomly(word_str)
        


        # Get all characters in the word (excluding slashes)
        word_chars = word_str[1:-1]  # Skip first and last characters (slashes)
        


        # Try to find intersections with existing words
        for existing_word_str, existing_word_obj in self._vocabulary_record.items():
            existing_row, existing_col = existing_word_obj.getPos()
            existing_is_horizontal = existing_word_obj.isHorizontal()
            existing_length = existing_word_obj.get_length()
            existing_word_chars = existing_word_str[1:-1]  # Skip slashes
            
            # Try to find common characters between the two words
            for i, char in enumerate(word_chars):
                for j, existing_char in enumerate(existing_word_chars):
                    if char == existing_char:
                        # Found a potential intersection point
                        
                        if existing_is_horizontal:
                            
                            new_row = existing_row - (i + 1) 
                            new_col = existing_col + (j + 1) 
                            new_is_horizontal = False
                            
                            # Check if the word would fit within grid boundaries
                            if new_row < 0 or new_row + len(word_str) > self._grid_height:
                                continue
                        else:
                            
                            new_row = existing_row + (j + 1) 
                            new_col = existing_col - (i + 1) 
                            new_is_horizontal = True
                            
                            
                            if new_col < 0 or new_col + len(word_str) > self._grid_width:
                                continue
                        
                        # Create a Word object for the new word
                        new_word_obj = Word(word_str, startPos=(new_row, new_col), 
                                        len=len(word_str), isHorizontal=new_is_horizontal)
                        
                        # Try to place the word
                        if self.place_word(new_word_obj):
                            return True
        
        # If no intersection was found or placement failed, try random positions
        return False




    def _place_word_randomly(self, word_str):
        """
        Try to place a word at random positions in the grid.
        Parameters:
        -----------
        word_str : str
            The word to place.
        Returns:
        --------
        bool
            True if the word was successfully placed, False otherwise.
        """
        max_attempts = 100
        
        for _ in range(max_attempts):
            # Randomly choose orientation
            is_horizontal = random.choice([True, False])
            
            # Choose random starting position
            if is_horizontal:
                row = random.randint(0, self._grid_height - 1)
                col = random.randint(0, self._grid_width - len(word_str))
            else:  # Vertical
                row = random.randint(0, self._grid_height - len(word_str))
                col = random.randint(0, self._grid_width - 1)
            
            # Create Word object with random position
            word_obj = Word(word_str, startPos=(row, col), len=len(word_str), isHorizontal=is_horizontal)
            
            # Try to place the word
            if self.place_word(word_obj):
                return True
        
        return False



    #Mutate the individual by removing and re-placing a random subset of words. Place words using intersections with existing words.
    #return  True if mutation was successful
    def mutate(self):
        if not self._vocabulary_record:
            return False
        
        # Determine how many words to mutate (between 10% and 30% of total words)
        num_words = len(self._vocabulary_record)
        num_to_mutate = max(1, random.randint(int(0.1 * num_words), int(0.3 * num_words)))
        
        # Select random words to mutate
        words_to_mutate = random.sample(list(self._vocabulary_record.keys()), num_to_mutate)
        original_grid = [row[:] for row in self._cross_word_grid]
        original_vocabulary_record = copy.deepcopy(self._vocabulary_record)
        
        # Remove selected words from the grid
        for word_str in words_to_mutate:
            self.remove_word(word_str)
        
        # Try to place the words back using intersection first, then random placement
        success = True
        for word_str in words_to_mutate:
            placed = self._place_word_with_intersection(word_str)
            if not placed:
                placed = self._place_word_randomly(word_str)
            # If still not placed, mark mutation as failed
            if not placed:
                success = False
                break
        
        # If mutation failed, restore original state
        if not success:
            self._cross_word_grid = original_grid
            self._vocabulary_record = original_vocabulary_record
            return False
        
        self.calculate_fitness()
        return True
    



    #Remove a word from the grid.
    #Parameters word_str : str The word to remove.
    def remove_word(self, word_str):

        if word_str not in self._vocabulary_record:
            return
        
        word_obj = self._vocabulary_record[word_str]
        row, col = word_obj.getPos()
        is_horizontal = word_obj.isHorizontal()
        length = word_obj.get_length()
        
        # Remove the word from the grid by replacing characters with ' '
        # but only if no other word uses that cell
        for i in range(length):
            if is_horizontal:
                pos_row, pos_col = row, col + i
            else:
                pos_row, pos_col = row + i, col
            
            # Check if this cell is used by any other word
            cell_used_by_other = False
            for other_word_str, other_word_obj in self._vocabulary_record.items():
                if other_word_str == word_str:
                    continue
                    
                other_row, other_col = other_word_obj.getPos()
                other_is_horizontal = other_word_obj.isHorizontal()
                other_length = other_word_obj.get_length()
                
                # Check if this cell is part of the other word
                for j in range(other_length):
                    if other_is_horizontal:
                        other_pos_row, other_pos_col = other_row, other_col + j
                    else:
                        other_pos_row, other_pos_col = other_row + j, other_col
                    
                    if pos_row == other_pos_row and pos_col == other_pos_col:
                        cell_used_by_other = True
                        break
                
                if cell_used_by_other:
                    break
            
            #Replace with ' ' 
            if not cell_used_by_other:
                self._cross_word_grid[pos_row][pos_col] = ' '
        del self._vocabulary_record[word_str]






    #Attempt to place a Word object in the grid at its specified position.
    # If the word cannot be placed, it returns False. If it can be placed,
    # it updates the grid and returns True.
    #word : Word   The Word object containing the word and its placement information.
    #Returns True if the word was successfully placed
    def place_word(self, word):

        word_str = word.getWord()
        
        # If the word already exists in the grid, remove it first
        if word_str in self._vocabulary_record:
            self.remove_word_from_grid(word_str)
        
        # Check if the placement is valid
        if not self._is_valid_placement(word):
            # If placement failed and the word was previously in the grid,
            # we need to restore the original word if possible
            if word_str in self._vocabulary_record:
                old_word = self._vocabulary_record[word_str]
                old_row, old_col = old_word.getPos()
                old_is_horizontal = old_word.isHorizontal()
                old_length = old_word.get_length()
                
                can_restore = True
                if old_is_horizontal:
                    for i in range(old_length):
                        if self._cross_word_grid[old_row][old_col + i] != ' ' and self._cross_word_grid[old_row][old_col + i] != word_str[i]:
                            can_restore = False
                            break
                else:  # Vertical
                    for i in range(old_length):
                        if self._cross_word_grid[old_row + i][old_col] != ' ' and self._cross_word_grid[old_row + i][old_col] != word_str[i]:
                            can_restore = False
                            break
                
                if can_restore:
                    # Restore the word
                    if old_is_horizontal:
                        for i in range(old_length):
                            self._cross_word_grid[old_row][old_col + i] = word_str[i]
                    else:  # Vertical
                        for i in range(old_length):
                            self._cross_word_grid[old_row + i][old_col] = word_str[i]
                    
                    return True
            return False
        # Place the word in the grid
        row, col = word.getPos()
        is_horizontal = word.isHorizontal()
        length = word.get_length()
        if is_horizontal:
            for i in range(length):
                self._cross_word_grid[row][col + i] = word_str[i]
        else:  # Vertical
            for i in range(length):
                self._cross_word_grid[row + i][col] = word_str[i]
        self._vocabulary_record[word_str] = word
        return True






    #Check if a Word object can be placed at its specified position.
    #If the placement is valid, the word is added to the grid.
    #If the placement is invalid, the function attempts to restore the original word if possible.
    #If the original word cannot be restored, the function returns False.
    #If the placement is valid and the word is successfully added to the grid, the function returns True.
    #word : Word   The Word object to check for valid placement.
    #Returns: bool True if the placement is valid and the word is successfully added to the grid, False otherwise.
    def _is_valid_placement(self, word):
        word_str = word.getWord()
        row, col = word.getPos()
        is_horizontal = word.isHorizontal()
        length = word.get_length()
        
        # Check if the word fits within grid boundaries
        if is_horizontal:
            if col + length > self._grid_width:
                return False
        else:  # Vertical
            if row + length > self._grid_height:
                return False
        
        

        for i in range(length):
            curr_row = row if is_horizontal else row + i
            curr_col = col + i if is_horizontal else col
            
            
            if (curr_row < 0 or curr_row >= self._grid_height or 
                curr_col < 0 or curr_col >= self._grid_width):
                return False
            
            # Get the current cell value
            curr_cell = self._cross_word_grid[curr_row][curr_col]
            if curr_cell != ' ' and curr_cell != word_str[i]:
                return False
        
        # Check for adjacent words of the same orientation
        for existing_word_str, existing_word in self._vocabulary_record.items():
            # Skip if it's the same word we're trying to place
            if word_str == existing_word_str:
                continue
            existing_row, existing_col = existing_word.getPos()
            existing_is_horizontal = existing_word.isHorizontal()
            existing_length = existing_word.get_length()
            
            # Only check words with the same orientation
            if is_horizontal == existing_is_horizontal:
                if is_horizontal:  # Both words are horizontal
                    # Check if they're on the same row or adjacent rows
                    if abs(row - existing_row) <= 1:
                        if not (col + length <= existing_col - 1 or col >= existing_col + existing_length + 1):
                            return False
                else:  # Both words are vertical
                    if abs(col - existing_col) <= 1:
                        if not (row + length <= existing_row - 1 or row >= existing_row + existing_length + 1):
                            return False
        
        return True

    #Remove a word from the grid by replacing its characters with ' '.
    #
    def remove_word_from_grid(self, word_str):
        #Parameters: The word to remove from the grid.
        if word_str not in self._vocabulary_record:
            return
        
        word_obj = self._vocabulary_record[word_str]
        row, col = word_obj.getPos()
        is_horizontal = word_obj.isHorizontal()
        length = word_obj.get_length()
        
        # Replace the word characters with ' '
        if is_horizontal:
            for i in range(length):
                # Only replace if this cell contains the expected character
                # This handles overlapping words correctly
                if self._cross_word_grid[row][col + i] == word_str[i]:
                    should_replace = True
                    for other_word, other_obj in self._vocabulary_record.items():
                        if other_word == word_str:
                            continue  # Skip the word we're removing
                        
                        other_row, other_col = other_obj.getPos()
                        other_is_horizontal = other_obj.isHorizontal()
                        other_length = other_obj.get_length()
                        
                        # Check if this position is part of another word
                        if other_is_horizontal:
                            if other_row == row and other_col <= col + i < other_col + other_length:
                                should_replace = False
                                break
                        else:  
                            if other_col == col + i and other_row <= row < other_row + other_length:
                                should_replace = False
                                break
                    
                    if should_replace:
                        self._cross_word_grid[row][col + i] = ' '
        else:  # Vertical
            for i in range(length):
                if self._cross_word_grid[row + i][col] == word_str[i]:
                    should_replace = True
                    for other_word, other_obj in self._vocabulary_record.items():
                        if other_word == word_str:
                            continue  # Skip the word we're removing
                        
                        other_row, other_col = other_obj.getPos()
                        other_is_horizontal = other_obj.isHorizontal()
                        other_length = other_obj.get_length()
                        
                        if other_is_horizontal:
                            if other_row == row + i and other_col <= col < other_col + other_length:
                                should_replace = False
                                break
                        else: 
                            if other_col == col and other_row <= row + i < other_row + other_length:
                                should_replace = False
                                break
                    
                    if should_replace:
                        self._cross_word_grid[row + i][col] = ' '





    def generate_children(self, other_parent):
        """
        Generate a child by combining words from two parents.
        If a word fails to be placed from either parent, try to place it
        intelligently by finding intersections with existing words.
        
        Parameters:
        -----------
        other_parent : Individual
            The second parent individual.
            
        Returns:
        --------
        Individual
            A new individual (child) created from the two parents.
        """
        # Create a new empty individual
        child = Individual(self._vocabulary_list)
        
        # Initialize the child's grid
        child._cross_word_grid = [[' ' for _ in range(child._grid_width)] for _ in range(child._grid_height)]
        
        # Get the vocabulary records from both parents
        parent1_words = list(self._vocabulary_record.keys())
        parent2_words = list(other_parent._vocabulary_record.keys())
        
        # Combine and shuffle all words to ensure random selection
        all_words = list(set(parent1_words + parent2_words))
        random.shuffle(all_words)
        
        # Place words in the child's grid
        for word_str in all_words:
            placed = False
            
            # Try to get the word from parent 1
            if word_str in parent1_words:
                word_obj = self._vocabulary_record[word_str]
                row, col = word_obj.getPos()
                is_horizontal = word_obj.isHorizontal()
                length = word_obj.get_length()
                
                # Create a new Word object for the child
                child_word = Word(
                    word_str,
                    startPos=(row, col),
                    len=length,
                    isHorizontal=is_horizontal
                )
                
                # Try to place the word in the child's grid
                if child.place_word(child_word):
                    placed = True
            
            # If not placed, try to get the word from parent 2
            if not placed and word_str in parent2_words:
                word_obj = other_parent._vocabulary_record[word_str]
                row, col = word_obj.getPos()
                is_horizontal = word_obj.isHorizontal()
                length = word_obj.get_length()
                
                # Create a new Word object for the child
                child_word = Word(
                    word_str,
                    startPos=(row, col),
                    len=length,
                    isHorizontal=is_horizontal
                )
                
                # Try to place the word in the child's grid
                if child.place_word(child_word):
                    placed = True
            
            # If still not placed, try to place it intelligently
            if not placed:
                # First try to place with intersection
                placed = child._place_word_with_intersection(word_str)
                
                # If that fails, try random placement
                if not placed:
                    placed = child._place_word_randomly(word_str)
                    
                # If still not placed, print a warning
                if not placed:
                    print(f"Warning: Could not place word '{word_str}' in the child grid")
        
        # Calculate fitness for the child
        child.calculate_fitness()
        
        return child






    # Fitness Functions calculations
    def calculate_fitness(self):
        final_fitness = 0;
        #intersection between words and '/'
        final_fitness += self.intersection_between_words();
        #empty row and columns
        final_fitness += self.fitness_empty_row_col();
        #word at central
        final_fitness += self.crossWord_at_central();
        #word at corner
        final_fitness += self.count_word_intersections();
        #word at corner
        final_fitness += self.calculate_occupied_area();
        #word at corner
        self.group_penalty = self.check_connected_components();
        final_fitness += self.group_penalty;
        self.fitness = final_fitness;
    
    def count_word_intersections(self):
        """
        Count the number of times each word intersects with other words.
        Each intersection adds 5 points to the score.
        Words with no intersections get a 15-point penalty.
        Intersections at '/' characters are not counted.
        Returns:
        --------
        int
            The calculated intersection score.
        """
        total_score = 0
        
        # Create a dictionary to track which positions have letters from which words
        # Key: (row, col) position, Value: list of words using this position
        position_to_words = {}
        for word_str, word_obj in self._vocabulary_record.items():
            start_row, start_col = word_obj.getPos()
            length = word_obj.get_length()
            is_horizontal = word_obj.isHorizontal()
            
            # Add each letter position to the position_to_words dictionary
            for i in range(length):
                # Skip the forward slash characters (first and last characters)
                if i == 0 or i == length - 1:
                    continue
                    
                if is_horizontal:
                    position = (start_row, start_col + i)
                else:
                    position = (start_row + i, start_col)
                
                # Get the character at this position
                char = self._cross_word_grid[position[0]][position[1]]
                # Skip if the character is a forward slash
                if char == '/':
                    continue
                    
                if position not in position_to_words:
                    position_to_words[position] = []
                
                position_to_words[position].append(word_str)
        # Count intersections for each word
        word_intersections = {word: 0 for word in self._vocabulary_record.keys()}
        
        for position, words in position_to_words.items():
            if len(words) > 1:  # This position is an intersection
                # For each word at this intersection, increment its intersection count
                for word in words:
                    word_intersections[word] += 1
        
        # Calculate score based on intersections
        for word, intersection_count in word_intersections.items():
            if intersection_count > 0:
                # Add 5 points for each intersection
                total_score += 5 * intersection_count
            else:
                # Subtract 35 points for words with no intersections
                total_score -= 35
        
        return total_score



    def get_occupied_cells(self, word):
        cells = []
        start_row, start_col = word.get_pos()
        length = word.get_length()

        if word.isHorizontal():
            for col in range(start_col, start_col + length):
                cells.append((start_row, col))
        else:
            for row in range(start_row, start_row + length):
                cells.append((row, start_col))
        return cells

    #Calculate fitness based on empty rows and columns.
    # An empty row or column is one where all cells contain ' ' or '/'.
    # Each empty row or column adds 5 points to the fitness.
    def fitness_empty_row_col(self):
        fitness = 0
        empty_chars = {' ', '/'}
        # Check for empty rows
        for row in range(self._grid_height):
            is_empty = True
            for col in range(self._grid_width):
                if self._cross_word_grid[row][col] not in empty_chars:
                    is_empty = False
                    break
            if is_empty:
                fitness += 2
        
        # Check for empty columns
        for col in range(self._grid_width):
            is_empty = True
            for row in range(self._grid_height):
                if self._cross_word_grid[row][col] not in empty_chars:
                    is_empty = False
                    break
            if is_empty:
                fitness += 2
        return fitness;

    #Calculate fitness based on the number of intersections between words.
    # Each intersection adds 15 points to the fitness.
    # If a word has no intersections, subtract 35 points from the fitness.
    def intersection_between_words(self):

        final_fitness = 0
        
        # Create a dictionary to track which positions have letters
        # Key: (row, col) position, Value: count of words using this position
        position_usage = {}
        
        # Populate the position_usage dictionary by traversing vocabulary_record
        for word, word_info in self._vocabulary_record.items():
            start_pos = word_info.getPos();
            length = word_info.get_length()
            is_horizontal = word_info.isHorizontal()

            # Skip words that weren't successfully placed
            if start_pos is None:
                continue
            row, col = start_pos
            
            # Add each letter position to the position_usage dictionary
            for i in range(length):
                if is_horizontal:
                    position = (row, col + i)
                else:
                    position = (row + i, col)
                
                if position not in position_usage:
                    position_usage[position] = 0
                    continue;
                # if position have use
                if position == start_pos:
                    final_fitness += 1;
                else:
                    if self._cross_word_grid[position[0]][position[1]] == '/':
                        final_fitness +=1;
                    else:
                        final_fitness += 15;
                #position_usage[position] += 1
        """"
        # Count intersections (positions used by more than one word)
        for position, count in position_usage.items():
            if count > 1:
                final_fitness += 10 * (count - 1)
        """
        
        return final_fitness





    def crossWord_at_central(self):
        """
        Calculate a score based on how close each word is to the center of the grid.
        Words closer to the center get higher scores.
        """
        # Get grid dimensions
        rows = len(self._cross_word_grid)
        cols = len(self._cross_word_grid[0]) if rows > 0 else 0
        
        # Calculate center positions
        center_row = rows // 2
        center_col = cols // 2
        
        total_score = 0
        max_distance = max(rows, cols) // 2  

        for word, word_obj in self._vocabulary_record.items():
            start_pos = word_obj.getPos()
            ishorizontal = word_obj.isHorizontal();
                
            if ishorizontal:
                    # For horizontal words, calculate distance from center row
                row_distance = abs(start_pos[0] - center_row)
                    # Calculate score: 10 points at center, decreasing as distance increases
                row_score = 10 * (1 - row_distance / max(max_distance, 1))
                total_score += row_score
            else:  # vertical
                col_distance = abs(start_pos[1] - center_col)
                col_score = 10 * (1 - col_distance / max(max_distance, 1))
                total_score += col_score
        return total_score





    # Check if all words in the crossword form a single connected component.  Words are only considered connected if they share actual letter intersections (not just slash characters).
    #If all words are in a single connected group, add 80 points.
    def check_connected_components(self):
        
        if len(self._vocabulary_record) <= 1:
            return 80  
        
        # Build a graph where words are nodes and intersections are edges
        word_graph = {}
        for word in self._vocabulary_record.keys():
            word_graph[word] = set()  
        
        position_to_words = {}
        
        # Populate the position_to_words dictionary (excluding slashes)
        for word_str, word_obj in self._vocabulary_record.items():
            start_row, start_col = word_obj.getPos()
            length = word_obj.get_length()
            is_horizontal = word_obj.isHorizontal()
            
            for i in range(1, length - 1):  
                if is_horizontal:
                    position = (start_row, start_col + i)
                else:
                    position = (start_row + i, start_col)
                
                # Get the character at this position
                char = self._cross_word_grid[position[0]][position[1]]
                
                # Skip if the character is a slash
                if char == '/':
                    continue
                    
                if position not in position_to_words:
                    position_to_words[position] = []
                position_to_words[position].append(word_str)
        
        # Build edges in the graph based on intersections
        for position, words in position_to_words.items():
            if len(words) > 1:  # This position is an intersection
                for i in range(len(words)):
                    for j in range(i + 1, len(words)):
                        word_graph[words[i]].add(words[j])
                        word_graph[words[j]].add(words[i])
        
        # Perform BFS to find connected components
        visited = set()
        components = []
        
        for word in word_graph:
            if word not in visited:
                component = []
                queue = [word]
                visited.add(word)
                
                while queue:
                    current = queue.pop(0)
                    component.append(current)
                    
                    for neighbor in word_graph[current]:
                        if neighbor not in visited:
                            visited.add(neighbor)
                            queue.append(neighbor)
                
                components.append(component)
        
        # Store the number of components for reference
        self.num_components = len(components)
        # If all words are in a single connected group, award 80 points
        if len(components) == 1 and len(components[0]) == len(self._vocabulary_record):
            self.groupPenalty = 80
            return 80
        else:
            self.groupPenalty = -20 * (len(components) - 1)
            # Additional penalty based on the size of isolated components
            for component in components:
                if len(component) == 1:  
                    self.groupPenalty -= 5  # Extra penalty for completely isolated words
            
            return self.groupPenalty




    #Calculate the area occupied by the crossword and reward more compact layouts.
    # 1. Finds the minimum bounding rectangle that contains all words
    # 2. Calculates the area of this rectangle
    # 3. Rewards layouts that use a smaller percentage of the total grid area
    def calculate_occupied_area(self):
        if not self._vocabulary_record:
            return 0
        
        # Initialize min/max coordinates to track the bounding box
        min_row = self._grid_height
        max_row = 0
        min_col = self._grid_width
        max_col = 0
        
        occupied_cells = set()
        
        for word_str, word_obj in self._vocabulary_record.items():
            start_row, start_col = word_obj.getPos()
            length = word_obj.get_length()
            is_horizontal = word_obj.isHorizontal()
            
            for i in range(length):
                if is_horizontal:
                    row, col = start_row, start_col + i
                else:
                    row, col = start_row + i, start_col
                
                # Update the bounding box
                min_row = min(min_row, row)
                max_row = max(max_row, row)
                min_col = min(min_col, col)
                max_col = max(max_col, col)
                
                # Add to occupied cells
                occupied_cells.add((row, col))
        
        # Calculate the area of the bounding box
        if min_row > max_row or min_col > max_col:  
            return 0
        # Calculate the total grid area 
        bounding_box_width = max_col - min_col + 1
        bounding_box_height = max_row - min_row + 1
        bounding_box_area = bounding_box_width * bounding_box_height
        
        total_grid_area = self._grid_width * self._grid_height
        
        # Calculate the density of the crossword within its bounding box
        num_occupied_cells = len(occupied_cells)
        density = num_occupied_cells / bounding_box_area if bounding_box_area > 0 else 0
        
        # Calculate the percentage of the grid used by the bounding box
        area_percentage = bounding_box_area / total_grid_area
        
        # Base score: up to 40 points for using less than 50% of the grid area
        area_score = 40 * (1 - min(area_percentage, 0.5) / 0.5)
        density_bonus = 20 * density
        
        compactness_score = int(area_score + density_bonus)
        
        return compactness_score



    ## debug method Display the crossword grid in a readable format.
    def print_grid(self):
        print('group penalty',self.group_penalty);

        print('==========Grid==========')
        for row in self._cross_word_grid:
            print(' '.join(row))