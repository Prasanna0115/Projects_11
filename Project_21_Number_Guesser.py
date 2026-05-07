import random

print("🎯 Welcome to the Guessing Game!")

# ---------------- INPUT ----------------
top_of_range = input("Type a number: ")

if not top_of_range.isdigit():
    print("❌ Please type a valid number.")
    quit()

top_of_range = int(top_of_range)

if top_of_range <= 0:
    print("❌ Number must be greater than 0.")
    quit()


# ================= SHARED SECRET =================
secret_number = random.randint(0, top_of_range)


# ================= USER GAME =================
print("\n==============================")
print("👤 USER GUESSING GAME START")
print("==============================")

user_guesses = 0

while True:
    user_guesses += 1
    user_guess = input("Make a guess: ")

    if not user_guess.isdigit():
        print("❌ Please type a number.")
        continue

    user_guess = int(user_guess)

    if user_guess == secret_number:
        print("✅ You got it!")
        break
    elif user_guess > secret_number:
        print("📉 Too high!")
    else:
        print("📈 Too low!")

print(f"🎉 You guessed it in {user_guesses} tries!")


# ================= COMPUTER GAME =================
print("\n==============================")
print("🤖 COMPUTER GUESSING GAME START")
print("==============================")

low = 0
high = top_of_range
computer_guesses = 0

while True:
    computer_guesses += 1

    computer_guess = random.randint(low, high)
    print(f"Computer guesses: {computer_guess}")

    if computer_guess == secret_number:
        print("🎯 Computer got it!")
        break
    elif computer_guess > secret_number:
        print("📉 Computer was high!")
        high = computer_guess - 1
    else:
        print("📈 Computer was low!")
        low = computer_guess + 1

print(f"🤖 Computer guessed it in {computer_guesses} tries!")


# ================= RESULT =================
print("\n==============================")
print("🏁 FINAL RESULT")
print("==============================")

if user_guesses < computer_guesses:
    print("🏆 You win!")
elif user_guesses > computer_guesses:
    print("🤖 Computer wins!")
else:
    print("🤝 It's a tie!")