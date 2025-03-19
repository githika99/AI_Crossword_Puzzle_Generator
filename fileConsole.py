# Not currently used in project
import os
import time

class fileConsole:
    #Gets the word list from the input folder according to the file name.
    def getVocabularyList(self, fileName):
        vocabulary = []
        
        try:
             
            file_path = os.path.join("input", fileName)
            
            # Open and read the file
            with open(file_path, 'r') as file:
                for line in file:
                    
                    word = line.strip()
                    if word:
                        vocabulary.append(word)
                        
            return vocabulary
        
        except FileNotFoundError:
            print(f"Error: File '{fileName}' not found in the input folder.")
            return []
        except Exception as e:
            print(f"Error reading vocabulary file: {e}")
            return []
        
    def CopyCrossWordGrid( self, wordGrid): 
        try:
            # Create output directory if it doesn't exist
            if not os.path.exists("output"):
                os.makedirs("output")
             
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            output_file = os.path.join("output", f"crossword_grid_{timestamp}.txt")
             
            with open(output_file, 'w') as file:
                for row in wordGrid: 
                    line = ''.join(row)
                    file.write(line + '\n')
                    
            print(f"Crossword grid successfully saved to {output_file}")
            
        except Exception as e:
            print(f"Error saving crossword grid: {e}")
