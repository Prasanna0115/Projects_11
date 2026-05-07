import random
board = [" "] * 9
def show():
    print()
    print(board[0] + " | " + board[1] + " | " + board[2])
    print("--+---+--")
    print(board[3] + " | " + board[4] + " | " + board[5])
    print("--+---+--")
    print(board[6] + " | " + board[7] + " | " + board[8])
    print()
def win(p):
    w = [(0,1,2),(3,4,5),(6,7,8),
         (0,3,6),(1,4,7),(2,5,8),
         (0,4,8),(2,4,6)]
    for a,b,c in w:
        if board[a] == board[b] == board[c] == p:
            return True
    return False
while True:
    show()
    move = int(input("Your move (1-9): ")) - 1
    if board[move] == " ":
        board[move] = "X"
    else:
        print("Already taken!")
        continue
    if win("X"):
        show()
        print("You win")
        break
    if " " not in board:
        show()
        print("Draw!")
    comp_move = random.choice([i for i in range(9) if board[i] == " "])
    board[comp_move] = "O"
    print("Computer played:", comp_move + 1)
    if win("O"):
        show()
        print("Computer wins")
        break
    if " " not in board:
        show()
        print("Draw!")
        break