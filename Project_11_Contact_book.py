print(" Simple Contact Book")
contacts = {}
while True:
    print("\n1. Add Contact")
    print("2. View Contacts")
    print("3. Search Contact")
    print("4. Delete Contact")
    print("5. Exit")
    choice = input("Enter choice: ")
    if choice == "1":
        name = input("Enter name: ")
        phone = input("Enter phone: ")
        contacts[name] = phone
        print("✅ Contact added")
    elif choice == "2":
        if not contacts:
            print("📭 No contacts found")
        else:
            for name, phone in contacts.items():
                print(name, ":", phone)
    elif choice == "3":
        name = input("Enter name to search: ")
        if name in contacts:
            print(name, ":", contacts[name])
        else:
            print(" Not found")
    elif choice == "4":
        name = input("Enter name to delete: ")
        if name in contacts:
            del contacts[name]
            print(" Deleted")
        else:
            print(" Not found")
    elif choice == "5":
        print(" Goodbye!")
        break
    else:
        print(" Invalid choice")