import random
item_list = ["Rock", "Paper", "Scissor"]
user_choice = input("Enter your move (Rock, Paper, Scissor): ").strip().capitalize()
comp_choice = random.choice(item_list)
print(f"\nUser choice = {user_choice}")
print(f"Computer choice = {comp_choice}\n")
if user_choice == comp_choice:
    print("Result: Match Tie")
elif user_choice == "Rock":
    if comp_choice == "Paper":
        print("Paper covers Rock → Computer Wins")
    else:
        print("Rock smashes Scissor → You Win")
elif user_choice == "Paper":
    if comp_choice == "Scissor":
        print("Scissor cuts Paper → Computer Wins")
    else:
        print("Paper covers Rock → You Win")
elif user_choice == "Scissor":
    if comp_choice == "Paper":
        print("Scissor cuts Paper → You Win")
    else:
        print("Rock smashes Scissor → Computer Wins")
else:
    print("Invalid input! Please enter Rock, Paper, or Scissor.")