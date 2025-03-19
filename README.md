By: Githika Annapureddy, Gavin Lebo, Peilin Huang, Christian Sigua

# Overview:
## This project is a crossword puzzle generator. The user is prompted to pick a theme, number of words, and difficulty level (1-12). The difficulty is based on the grades 1 through 12. 
## A genetic algorithm to create a crossword puzzle based on these parameters. The fitness is calculated based on the number of intersections between words in puzzle, how close the crossword is to the center of the grid, if all words in crossword are connected, how many empty rows/cols there are. Natural Language Toolkit (NLTK) is used to generate the words with context-based similarity. OpenAI's gpt-4o mini model is used to set the difficulty of the words and generate the prompts. 

# To Play: 
## $ pip install -r requirements.txt #to install requirements
## $ pip install nltk 
## $ python3 nltk_setup.py #to get dependencies
