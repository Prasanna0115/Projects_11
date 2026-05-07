tasks = []
while True:
    print("\n TO-DO APP")
    print("1. Add Task")
    print("2. View Tasks")
    print("3. Delete Task")
    print("4. Exit")
    choice = input("Enter choice: ")
    if choice == "1":
        task = input("Enter task: ")
        tasks.append(task)
        print(" Added")
    elif choice == "2":
        if not tasks:
            print(" No tasks")
        else:
            for i in tasks:
                print("-", i)
    elif choice == "3":
        task = input("Enter task to delete: ")
        if task in tasks:
            tasks.remove(task)
            print(" Deleted")
        else:
            print(" Not found")
    elif choice == "4":
        print(" Bye!")
        break
    else:
        print(" Invalid choice")