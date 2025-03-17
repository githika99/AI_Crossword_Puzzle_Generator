import openai

def get_crossword_hints(theme, words, difficulty):
    hints = {}
    for word in words:
        prompt = f"Provide a short crossword-style hint for the word '{word}', given that the theme of the puzzle is '{theme}', and the intended audience for the crossword is of education level Grade {difficulty}:"
        
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": "You are an expert at creating crossword puzzle hints. Do not include the letter amount in the hint."},
                      {"role": "user", "content": prompt}],
            max_tokens=30,
            temperature=0.7
        )
        
        hint = response["choices"][0]["message"]["content"].strip()
        hints[word] = hint
    
    return hints

#test
# words = ["structure", "technique", "discipline", "process", "buildings", "creation", "edifice"]
# crossword_hints = get_crossword_hints(words)
# for key, value in crossword_hints.items():
#     print(f"{key}: {value}")
#print(crossword_hints)

