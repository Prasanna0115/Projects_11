students = {}

def add_student():
    name = input("Enter student name: ").strip()

    marks = []
    subjects = ["Math", "Science", "English"]

    for subject in subjects:
        mark = int(input(f"Enter marks in {subject}: "))
        marks.append(mark)

    total = sum(marks)
    percentage = total / len(subjects)

    if percentage >= 75:
        grade = "A"
    elif percentage >= 60:
        grade = "B"
    elif percentage >= 40:
        grade = "C"
    else:
        grade = "Fail"

    students[name] = {
        "marks": marks,
        "total": total,
        "percentage": percentage,
        "grade": grade
    }

    print("Student added successfully!\n")

def view_students():
    if not students:
        print("No student records found.\n")
        return

    for name, data in students.items():
        print(f"\nName: {name}")
        print(f"Marks: {data['marks']}")
        print(f"Total: {data['total']}")
        print(f"Percentage: {data['percentage']:.2f}%")
        print(f"Grade: {data['grade']}")

def main():
    while True:
        print("\n--- Student Result Manager ---")
        print("1. Add Student")
        print("2. View Students")
        print("3. Exit")

        choice = input("Enter choice: ")

        if choice == "1":
            add_student()
        elif choice == "2":
            view_students()
        elif choice == "3":
            print("Goodbye!")
            break
        else:
            print("Invalid choice!")

main()