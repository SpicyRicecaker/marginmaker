# coding: magic.braces
# from tkinter import *
from tkinter import ttk
# root = Tk()
# frm = ttk.Frame(root, padding=10)
# frm.grid()
# ttk.Label(frm, text="Hello World!").grid(column=0, row=0)
# ttk.Button(frm, text="Quit", command=root.destroy).grid(column=1, row=0)
# root.mainloop()
# 
import tkinter as tk
from tkinterdnd2 import DND_FILES, TkinterDnD

def instafocus(window) {
    # 1. Force the window to the very top layer
    window.attributes('-topmost', True)
    
    # 2. Lift it above everything else
    window.lift()
    
    # 3. Forcefully grab system focus 
    # window.focus_force()
    
    # 4. Release the "always on top" behavior after an idle cycle, 
    # so the user can still put other windows over it if they want.
    window.after_idle(window.attributes, '-topmost', False)
}
    

def init_gui() {
    root = TkinterDnD.Tk()  # notice - use this instead of tk.Tk()
    root.geometry("400x300")

    {
     frm0 = ttk.Frame(root, padding=10)
    #     frm0.pack()

    #     # {
    #     #     frm = ttk.Frame(frm0, padding=10)
    #     #     frm.grid()

    #     #     {
    #     #         ttk.Label(frm, text="Drop file here!").grid(column=0, row=0)
    #     #     }

    #     #     {
    #     #         lb = tk.Listbox(frm, width=30, height=20)
    #     #         lb.grid(column=0, row=1)
    #     #         def on_drop(event) {
    #     #             # event.data is a raw Tcl list string, not a Python list - see note below
    #     #             for path in root.tk.splitlist(event.data) {
    #     #                 lb.insert(tk.END, path)
    #     #             }
    #     #         }
    #     #         lb.drop_target_register(DND_FILES)
    #     #         lb.dnd_bind('<<Drop>>', on_drop)
    #     #     }
    #     # }
    }
    
    instafocus(root)
    return root
}

def main() {
    root = init_gui()
    root.mainloop()
}

if __name__ == "__main__" {
    main()
}
