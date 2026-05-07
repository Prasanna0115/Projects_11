import random
import string
passwords = {}
def generate_password(length=8):
    chars = string.ascii_letters + string.digits + string.punctuation
    return "".join(random.choice(chars) for i in range(length))
while True:
    print("\n--- PASSWORD MANAGER ---")
    print("1. Add Password")
    print("2. View Passwords")
    print("3. Generate Password")
    print("4. Exit")
    choice = input("Enter choice: ")
    if choice == "1":
        website = input("Enter website: ")
        password = input("Enter password: ")
        passwords[website] = password
        print("Password Saved!")
    elif choice == "2":
        if not passwords:
            print("No passwords stored.")
        else:
            print("\nSaved Passwords:")
            for website, password in passwords.items():
                print(f"{website} : {password}")
    elif choice == "3":
        length = int(input("Enter password length: "))
        print("Generated Password:", generate_password(length))
    elif choice == "4":
        print("Exiting...")
        break
    else:
        print("Invalid Choice!")