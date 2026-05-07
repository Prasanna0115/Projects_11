students = {}
while True:
    print("\n----- STUDENT MANAGER APP -----")
    print("1. Add Student")
    print("2. View Students")
    print("3. Check Result")
    print("4. Exit")
    choice = input("Enter your choice: ")
    if choice == "1":
        name = input("Enter student name: ")
        marks = int(input("Enter marks: "))
        students[name] = marks
        print(f"{name} Successfully Added!")
    elif choice == "2":
        if not students:
            print("No student records found.")
        else:
            print("\nStudent Records:")
            for name, marks in students.items():
                print(f"Name: {name} | Marks: {marks}")
    elif choice == "3":
        name = input("Enter student name to check result: ")
        if name in students:
            marks = students[name]
            print(f"\nStudent Name: {name}")
            print(f"Marks: {marks}")
            if marks >= 75:
                print("Grade: A")
                print("Result: Pass")
            elif marks >= 60:
                print("Grade: B")
                print("Result: Pass")
            elif marks >= 40:
                print("Grade: C")
                print("Result: Pass")
            else:
                print("Grade: Fail")
                print("Result: Fail")
        else:
            print("Student not found!")
    elif choice == "4":
        print("Exiting App...")
        break
    else:
        print("Invalid Choice!")