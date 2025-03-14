
from fileConsole import fileConsole

import similar
from individual import Individual
import copy
import random
import heapq
class CrossWordGridGenerator(object):

    def __init__(self, list = []):
        #Parameters: list or str, optional list of words to use as vocabulary or a filename to load words from.    
        self._vocabularyList = list;
        self._population = [];
        self._count = 100;
        self._succsetor = None;
        self.loopCounter = 0;
        self.groupPenalty = 0;
    


    def generate_population(self):
        """
        Generate a population of Individual objects and store them in a heap queue.
        The heap is ordered by fitness 
        """
        # Clear existing population if any
        self._population = []
        
        # Generate the specified number of individuals
        counter = 0  
        for _ in range(self._count):
            individual = Individual(self._vocabularyList)
            heapq.heappush(self._population, individual);
            counter += 1
        
        ##debug
        print(f"Generated population of {len(self._population)} individuals")
        self.print_best_grid();
        
        
        """
        Generate the next generation of population using various genetic operations:
        - Elite selection (top 10%)
        - Hybridization (next 50%)
        - Mutation (next 20%)
        - Random selection from lower 50% (remaining)
        """
    def generate_successors(self):
        
        population_size = len(self._population)
        elite_size = int(0.1 * population_size)  # Top 10%
        hybridization_size = int(0.5 * population_size)  # Next 50%
        mutation_size = int(0.2 * population_size)  # Next 20%
        random_selection_size = population_size - elite_size - hybridization_size - mutation_size  # Remaining
        
        # Extract all individuals from the heap
        original_population = copy.deepcopy(self._population);
        
        new_population = []
        
        # Keep Elite individuals (top 10%)
        elite = original_population[:elite_size]
        for e in elite:
            #new_population.extend(elite)
            heapq.heappush(new_population, e);
        # Hybridization for next 50%
        for _ in range(hybridization_size):
            # Select two parents from the top 60% (elite + hybridization candidates)
            parent1 = random.choice(original_population[:int(0.6 * population_size)])
            parent2 = random.choice(original_population[:int(0.6 * population_size)])
            
            # Generate child
            child = parent1.generate_children(parent2)
            
            heapq.heappush(new_population, child);
        # Mutation (next 20%)
        mutation_candidates = original_population[elite_size:elite_size + hybridization_size]
        for _ in range(mutation_size):
            # Select an individual to mutate
            individual = copy.deepcopy(random.choice(mutation_candidates))
            
            # Mutate
            individual.mutate()
            
            heapq.heappush(new_population, individual);
        # Fill remaining with random individuals from the lower 50% of original population
        lower_half = original_population[int(0.5 * population_size):]
        for _ in range(random_selection_size):
            individual = copy.deepcopy(random.choice(lower_half))
            #new_population.append(individual)
            heapq.heappush(new_population, individual);
            
        """""
        self._population = []
        for individual in new_population:
            heapq.heappush(self._population, individual)
        
        # Debug
        print(f"Generated successor population of {len(self._population)} individuals")
        self.print_best_grid()
        """
        return new_population;



    


    #Execute the genetic algorithm to find the best crossword grid configuration.      
    #max_fitness =-1(not use) Not recommand Max fitness: when the fitness reach the max fitness will return the best individual
    #stop loop = 300 Recommand The algorithm stops running when the fitness does not increase after more than 300 cycles.
    #Returns: Individual: The best individual with the highest fitness.
    def ga(self, max_fitness= -1, stop_loop = 300):
        if not self._vocabularyList:
            raise ValueError("Vocabulary list must be set before running GA.")
        
        loopCounter = 0
        stop_counter = 0
        # Initialize the population
        self.generate_population()
        #best_negative_fitness1, _, parent1 = self._population[0]
        succestor = self._population[0];
        fitness = succestor.getFitness();
        # Genetic algorithm loop
        while True:
            # Generate new population
            current_best = None;
            self._population = self.generate_successors();
            current_best = self._population[0];
            loopCounter += 1
            stop_counter += 1
            #self.print_best_grid();
            # Update the best individual
            print(f"=====Loop:{loopCounter} Current Best Fitness: {current_best.getFitness()} =====")
            if current_best.getFitness() > succestor.getFitness():
                succestor = current_best;
                fitness = succestor.getFitness();
                self.print_best_grid();
                stop_counter = 0;
            

            if max_fitness != -1 and fitness >= max_fitness:
                break;
            
            if stop_counter >= stop_loop:
                break;
        self._succsetor = succestor;    
        return succestor;

    



    #set the population
    def setCount(self, c):
        self._count = c;



    #Set the vocabulary list.
    def setVocabularyList(self, l):   
        #Parameters: l : list List of words to use as vocabulary.
        self._vocabularyList = l


    # Gets the vocabulary list from the input folder according to the file name.
    def setVocabularyListOS(self, fileName):
        fc = fileConsole()
        self._vocabularyList = fc.getVocabularyList(fileName)
    


    #Remove empty rows and columns from the grid to create a more compact layout.
    #Parameters individual object
    def scissors(self, successor):
        #Returns:  A new grid with empty rows and columns removed.
        # Get dimensions of the original grid
        original_height = successor.get_height()
        original_width = successor.get_width()
        grid = successor._cross_word_grid;
        # Find non-empty rows
        non_empty_rows = []
        for row in range(original_height):
            is_empty = True
            for col in range(original_width):
                if grid[row][col] not in ['.', '/']:
                    is_empty = False
                    break
            if not is_empty:
                non_empty_rows.append(row)
        
        # Find non-empty columns
        non_empty_cols = []
        for col in range(original_width):
            is_empty = True
            for row in range(original_height):
                if grid[row][col] not in ['.', '/']:
                    is_empty = False
                    break
            if not is_empty:
                non_empty_cols.append(col)
        
        # If no content was found, return a minimal grid
        if not non_empty_rows or not non_empty_cols:
            return [['.']]
        
        new_height = len(non_empty_rows)
        new_width = len(non_empty_cols)
        cross_word_grid = [['.' for _ in range(new_width)] for _ in range(new_height)]
        
        # Copy content from the original grid to the new grid
        for new_row, orig_row in enumerate(non_empty_rows):
            for new_col, orig_col in enumerate(non_empty_cols):
                cross_word_grid[new_row][new_col] = grid[orig_row][orig_col]
        
        return cross_word_grid





    #get cross word grid as 2d array
    def get_cross_word_grid(self, stop_loop = 350 ,max_fitness= -1 ,re_generate = False):
        if self._vocabularyList == []:
            return None;
        succestor = self._succsetor;

        if re_generate or succestor is None:
            succestor = self.ga(max_fitness,stop_loop);
        return self.scissors(succestor);

    #get txt file of grid
    def get_cross_word_gridOS(self, stop_loop = 350 ,max_fitness= -1,re_generate = False):
        if self._vocabularyList == []:
            return None;
        succestor = self._succsetor;

        if re_generate or succestor is None:
            succestor = self.ga(max_fitness,stop_loop);
        fc = fileConsole()
        fc.CopyCrossWordGrid(self.scissors(succestor));



    #debug method pring best grid
    def print_best_grid(self):
        if self._population:
            best_individual = self._population[0]  
            print(f"Best individual fitness: {best_individual.getFitness()}")
            best_individual.print_grid()  
    
    #debug method Print the vocabulary List (debug)
    def print_vocabularyList(self):
        # print origin theme
        print(f"=====Theme: {theme}=====")
        # Print each word directly
        print('========Vocabulary=========')
        for word in self._vocabularyList:
            print(word)

    # debug method
    def test_child(self):
        
        if len(self._population) < 2:
            print("Need at least 2 individuals in the population to test child generation.")
            return
        parent1 = self._population[0]
        parent2 = self._population[1]


        print("Parent 1 (Fitness: {:.2f}):".format(parent1.getFitness()))
        parent1.print_grid()
        print("\nParent 2 (Fitness: {:.2f}):".format(parent2.getFitness()))
        parent2.print_grid()
        
        
        child = parent1.generate_children(parent2)
        
        
        print("\nChild (Fitness: {:.2f}):".format(child.getFitness()))
        child.print_grid();
    


    #debug method
    def test_mutate(self):
        #Test the mutation
        if not self._population:
            print("Population is empty. Cannot test mutation.")
            return
        print("\nPerforming mutation...")
        best_individual = self._population[0]
        
        mutated_individual = copy.deepcopy(best_individual)
        
        # Print
        print("Original Individual (Fitness: {:.2f}):".format(best_individual.getFitness()))
        best_individual.print_grid();
        
        
        
        success = mutated_individual.mutate()
        if(success):
            print('success')
        # Print the result
        print("\nMutated Individual (Fitness: {:.2f}):".format(mutated_individual.getFitness()))
        mutated_individual.print_grid()


#debug method
def print_grid(grid):
    
    
    # Get dimensions
    height = len(grid)
    width = len(grid[0])
    
    print("   ", end="")
    for col in range(width):
        print(f"{col % 10} ", end="")
    print()
    
    # Print top border
    print("  +" + "-" * (width * 2 - 1) + "+")
    
    # Print grid with row indices
    for row in range(height):
        print(f"{row % 10} |", end="")
        for col in range(width):
            print(f"{grid[row][col]} ", end="")
        print("|")
    
    print("  +" + "-" * (width * 2 - 1) + "+")

theme = input("Please choose a theme:\n")
wordCount = int(input("How many words?\n"))

generator = CrossWordGridGenerator();
generator.setVocabularyList(similar.getWords(theme, wordCount)); # use similar.py to get a theme and some words
generator.setCount(100);
g = generator.get_cross_word_grid(30)
generator.print_vocabularyList();
print_grid(g);
generator.get_cross_word_gridOS()
"""
generator.print_vocabularyList();
generator.generate_population();
generator.print_best_grid();
generator.test_child();
generator.test_mutate();
"""