import json

FILE = "todo_list.json"
def load_tasks():
    try:
        return json.load(open(FILE))
    except:
        return {"tasks": []}
def save_tasks(tasks):
    json.dump(tasks, open(FILE, "w"))

def view_tasks(tasks):
    if not tasks["tasks"]:
        print("No tasks.")
        return
    for i, task in enumerate(tasks["tasks"], 1):
        status = "Done" if task["complete"] else "Pending"
        print(f"{i}. {task['description']} ({status})")
def add_task(tasks):
    desc = input("Task: ").strip()
    if desc:
        tasks["tasks"].append({"description": desc, "complete": False})
        save_tasks(tasks)
def complete_task(tasks):
    view_tasks(tasks)
    try:
        i = int(input("Task number: ")) - 1
        tasks["tasks"][i]["complete"] = True
        save_tasks(tasks)
    except:
        print("Invalid input")
def main():
    tasks = load_tasks()
    while True:
        print("\n1.View  2.Add  3.Complete  4.Exit")
        choice = input("Choice: ")
        if choice == "1":
            view_tasks(tasks)
        elif choice == "2":
            add_task(tasks)
        elif choice == "3":
            complete_task(tasks)
        elif choice == "4":
            break
main()