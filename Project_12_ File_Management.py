import os
while True:
    print("\n File Manager")
    print("1. Create file")
    print("2. Write file")
    print("3. Read file")
    print("4. Delete file")
    print("5. Exit")
    choice = input("Enter choice: ")
    if choice == "1":
        name = input("File name: ")
        open(name, "w").close()
        print(" File created")
    elif choice == "2":
        name = input("File name: ")
        text = input("Text: ")
        with open(name, "a") as f:
            f.write(text + "\n")
        print(" Written")
    elif choice == "3":
        name = input("File name: ")
        try:
            with open(name, "r") as f:
                print("\n Content:")
                print(f.read())
        except:
            print(" File not found")
    elif choice == "4":
        name = input("File name: ")
        try:
            os.remove(name)
            print(" Deleted")
        except:
            print(" File not found")
    elif choice == "5":
        print(" Bye!")
        break
    else:
        print(" Invalid choice")