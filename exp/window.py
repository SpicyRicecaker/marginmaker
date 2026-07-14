# from tkinter import *
# from tkinter import ttk
# root = Tk()
# frm = ttk.Frame(root, padding=10)
# frm.grid()
# ttk.Label(frm, text="Hello World!").grid(column=0, row=0)
# ttk.Button(frm, text="Quit", command=root.destroy).grid(column=1, row=0)
# root.mainloop()
# 
import tkinter as tk
from tkinterdnd2 import DND_FILES, TkinterDnD

root = TkinterDnD.Tk()  # notice - use this instead of tk.Tk()

lb = tk.Listbox(root)
lb.insert(1, "drag files to here")

def on_drop(event):
    # event.data is a raw Tcl list string, not a Python list - see note below
    for path in root.tk.splitlist(event.data):
        lb.insert(tk.END, path)

# register the listbox as a drop target
lb.drop_target_register(DND_FILES)
lb.dnd_bind('<<Drop>>', on_drop)

lb.pack()
root.mainloop()
