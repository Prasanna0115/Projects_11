from tkinter import *
from tkinter import filedialog
def open_file():
    file = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
    if file:
        with open(file, "r") as f:
            text.delete(1.0, END)
            text.insert(1.0, f.read())
def save_file():
    file = filedialog.asksaveasfilename(defaultextension=".txt",
                                         filetypes=[("Text Files", "*.txt")])
    if file:
        with open(file, "w") as f:
            f.write(text.get(1.0, END))
root = Tk()
root.title("Text Editor")
root.geometry("600x400")
text = Text(root)
text.pack(expand=True, fill=BOTH)
Button(root, text="Open", command=open_file).pack(side=LEFT)
Button(root, text="Save", command=save_file).pack(side=LEFT)
root.mainloop()