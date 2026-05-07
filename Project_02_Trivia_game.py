import random

questions = {
    "What keyword is used to define a class in Python?": "class",
    "Which function is used to display output in Python?": "print",
    "Which operator is used for equality comparison?": "==",
    "What keyword is used for conditional statements?": "if",
    "What is the result of 5 % 2?": "1",
    "Which keyword is used to exit a loop?": "break",
    "What is used to handle exceptions in Python?": "try",
    "What built-in function converts a string to an integer?": "int",
    "What symbol is used for exponentiation in Python?": "**",
    "Which data type is ordered and immutable?": "tuple",
    "What keyword is used to return a value from a function?": "return",
    "Which method is used to add an item to a list?": "append",
    "What does 'None' represent in Python?": "null",
    "Which keyword is used to create a loop that runs while a condition is true?": "while",
    "What function is used to get the type of a variable?": "type",
    "Which keyword is used to skip the current iteration in a loop?": "continue",
    "What is the result of 9 // 2?": "4",
    "Which data type stores key-value pairs?": "dictionary",
    "What keyword is used to define an anonymous function?": "lambda",
    "Which method removes all items from a list?": "clear"
}

def python_trivia_game():
    questions_list = list(questions.keys())
    total_questions = 5
    score = 0

    selected_questions = random.sample(questions_list, total_questions)

    for idx, question in enumerate(selected_questions):
        print(f"{idx + 1}. {question}")
        user_answer = input("Your answer: ").lower().strip()
        correct_answer = questions[question]

        if user_answer == correct_answer.lower():
            print("Correct!\n")
            score += 1
        else:
            print(f"Wrong. The correct answer is: {correct_answer}.\n")

    print(f"Game over! Your final score is: {score}/{total_questions}")

python_trivia_game()