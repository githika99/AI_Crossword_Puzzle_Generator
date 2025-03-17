import openai

def change_difficulty(words, diff):
    # difficulty here is a number 1-12 representing 1st-12th grade reading level
    gradeWords = []
    for word in words:
        prompt = f"Replace the word '{word}' with an equivalent word for a {diff}th reading level:"
        
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": f"Take the role of a teacher teaching Grade {diff} students. Do not include anything other than the new word."},
                      {"role": "user", "content": prompt}],
            max_tokens=30,
            temperature=0.7
        )
        
        gradeLevelWord = response["choices"][0]["message"]["content"].strip()
        gradeWords.append(gradeLevelWord)
    
    return gradeWords

#test
# words = ["structure", "technique", "discipline", "process", "buildings", "creation", "edifice"]
# new_words = change_difficulty(words, 1)
# for key, value in new_words.items():
#     print(f"{key}: {value}")
#print(crossword_hints)

