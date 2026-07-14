import tkinter as tk
from tkinter import Entry, StringVar
from tkinter.ttk import Frame, Label, Button
import tkinter.ttk as ttk
from tkinterdnd2 import DND_FILES, TkinterDnD

def instafocus(window):
    # 1. Force the window to the very top layer
    window.attributes("-topmost", True)
    
    # 2. Lift it above everything else
    window.lift()
    
    # 3. Forcefully grab system focus 
    # window.focus_force()
    
    # 4. Release the "always on top" behavior after an idle cycle, 
    # so the user can still put other windows over it if they want.
    window.after_idle(window.attributes, "-topmost", False)

def init_gui():
    root = TkinterDnD.Tk()  # Notice - use this instead of tk.Tk()
    root.geometry("500x400")

    margin_str = StringVar(root)

    frm0 = ttk.Frame(root, padding=10)
    frm0.pack()

    frm = ttk.Frame(frm0, padding=10)
    frm.grid()

    label1 = ttk.Label(frm, text="Drop file here!")
    label1.grid(column=0, row=0)

    lb = tk.Listbox(frm, width=30, height=20)
    lb.grid(column=0, row=1)

    def on_drop(event):
        # event.data is a raw Tcl list string, not a Python list
        for path in root.tk.splitlist(event.data):
            lb.insert(tk.END, path)

    lb.drop_target_register(DND_FILES)
    lb.dnd_bind("<<Drop>>", on_drop)

    instafocus(root)
    
    cv = ttk.Button(frm, text="Convert selected pdf")
    cv.grid(column=1, row=0)

    # mg = ttk.Label(frm, text="Margin sides")
    # mg.grid(column=1, row=1)

    frm2 = ttk.Frame(frm, padding=0)
    frm2.grid(column=1, row=1)

    mg = ttk.Label(frm2, text="Margin sides")
    mg.grid(column=0, row=0)

    mg_txt = ttk.Entry(frm2, textvariable=margin_str)
    mg_txt.grid(column=0, row=1)
    mg_txt.insert(0, "500")

    def on_change(*args):
        print(margin_str.get())

    # In Python, trace_add takes (mode, callback) and callback receives standard args (*args)
    margin_str.trace_add("write", on_change)

    return root

def main():
    root = init_gui()
    root.mainloop()

if __name__ == "__main__":
    main()