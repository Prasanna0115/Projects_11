import difflib
print("🔤 Welcome to Auto-Correct System!")
print("Type a sentence and I will fix spelling mistakes.\n")
dictionary = [
    "python", "flask", "database", "computer", "programming",
    "developer", "internet", "machine", "learning", "backend",
    "frontend", "application", "function", "variable", "syntax",
    "debug", "algorithm", "code", "error", "server"
]
def correct_word(word):
    word = word.lower()
    matches = difflib.get_close_matches(word, dictionary, n=1, cutoff=0.6)
    if matches:
        return matches[0]
    else:
        return word  # if no match found, return original word
sentence = input("Enter sentence: ")
words = sentence.split()
corrected_words = []
for word in words:
    corrected = correct_word(word)
    corrected_words.append(corrected)
corrected_sentence = " ".join(corrected_words)
print("\n==============================")
print("✏️ Corrected Sentence:")
print("==============================")
print(corrected_sentence)