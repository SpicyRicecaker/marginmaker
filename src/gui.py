import tkinter as tk
from tkinter import Entry, StringVar
from tkinter.ttk import Frame, Label, Button
import tkinter.ttk as ttk
from tkinterdnd2 import DND_FILES, TkinterDnD
from scale import convert
import ast

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

def set_width_child(tk_element, width_child):
   for c in range(width_child):
      tk_element.columnconfigure(c, weight=1)

def set_height_child(tk_element, height_child):
   for r in range(height_child):
      tk_element.rowconfigure(r, weight=1)

class App():
    def __init__(self):
      self.margin = 500

      self.root = TkinterDnD.Tk()  # Notice - use this instead of tk.Tk()
      # self.root.geometry("500x400")
      self.root.title("Margin X-Spandr+🍎🍎🍎🍎🍎")
      self.root.columnconfigure(0, weight=1)
      self.root.rowconfigure(0, weight=1)
      

      body = ttk.Frame(self.root, borderwidth=5, relief="ridge", width=400, height=300)
      body.grid(column=0, row=0)
      set_width_child(body, 23)
      set_height_child(body, 20)

      if True:
        f_portrait = ttk.Frame(body, borderwidth=5, relief="ridge")
        f_portrait.grid(column=4, row=2, columnspan=18, rowspan=17)
        set_width_child(f_portrait, 18)
        set_height_child(f_portrait, 17)

        f_dropbox = ttk.Frame(f_portrait)
        f_dropbox.grid(column=0, row=0, columnspan=18, rowspan=12)
        set_width_child(f_dropbox, 18)
        set_height_child(f_dropbox, 12)

        f_margin = ttk.Frame(f_portrait)
        f_margin.grid(column=0, row=12, columnspan=18, rowspan=2)
        set_width_child(f_margin, 18)

        f_convert = ttk.Frame(f_portrait)
        f_convert.grid(column=0, row=14, columnspan=18, rowspan=3)
        set_width_child(f_convert, 18)
        set_height_child(f_convert, 3)

        label_dropbox = ttk.Label(f_dropbox, text="Drop PDF below:")
        label_dropbox.grid(column=0, row=0, columnspan=18, rowspan=2)
        self.listvar = StringVar()
        def on_change(*args):
          print(self.listvar.get())
        self.listvar.trace_add("write", on_change)
        self.list_dropbox = tk.Listbox(f_dropbox, listvariable=self.listvar)
        self.list_dropbox.grid(column=0, row=2, rowspan=10)
        def on_drop(event):
            # event.data is a raw Tcl list string, not a Python list
            for path in self.root.tk.splitlist(event.data):
                self.list_dropbox.insert(tk.END, path)
            self.list_dropbox.selection_set(tk.END)
        self.list_dropbox.drop_target_register(DND_FILES)
        self.list_dropbox.dnd_bind("<<Drop>>", on_drop)

        label_margin = ttk.Label(f_margin, text="Margin")
        label_margin.grid(column=0, row=0, columnspan=6)
        self.margin_str = StringVar(self.root)
        entry_margin = ttk.Entry(f_margin, textvariable=self.margin_str)
        entry_margin.grid(column=6, row=0, columnspan=6)
        entry_margin.insert(0, "500")
        def on_change(*args):
            print(self.margin_str.get())
        self.margin_str.trace_add("write", on_change)
        btn_margin = ttk.Button(f_margin, text="Live preview")
        btn_margin.grid(column=12, row=0, columnspan=6)

        btn_convert = ttk.Button(f_convert, text="Convert selected pdf", command=self.on_mousedown)
        btn_convert.grid(column=4, row=2, columnspan=10, rowspan=2)
        # BIGDESCRIPTION = ttk.Label(frm, text="HAVE YOU EVER WANTED TO CONVERT YOUR PDFS? WELL NOW INTRODUCING ooops caps MARGIN X-SPANDR+!" \
        # "NOW YOU CAN SPEAK BACK AGAINST THESE TEXTBOOK AUTHORS" \
        # "EXPRESS YOUR OPINION" \
        # "AND REACH YOUR OWN CONCLUSIONS" \
        # "NOW ONLY FREE")
        # BIGDESCRIPTION.grid(column=0, row=2)


      
      # In Python, trace_add takes (mode, callback) and callback receives standard args (*args)
      # self.list_dropbox.grid(column=1, row=1)


      instafocus(self.root)
      
      # mg = ttk.Label(frm, text="Margin sides")
      # mg.grid(column=1, row=1)

      # frm2 = ttk.Frame(frm, padding=0)
      # frm2.grid(column=0, row=0)

      # mg = ttk.Label(frm2, text="Margin sides")
      # mg.grid(column=0, row=0)

      # mg_txt = ttk.Entry(frm2, textvariable=self.margin_str)
      # mg_txt.grid(column=0, row=1)
      # mg_txt.insert(0, "500")

      # In Python, trace_add takes (mode, callback) and callback receives standard args (*args)


    def run(self):
        self.root.mainloop()

    def on_mousedown(self):
       print('hiiiiiiiiiiiiiiiiiiiiiiiii')
       # non_numeric = False
       # for c in '0123456789'.split(''):
       self.margin = int(self.margin_str.get())

       i = self.list_dropbox.curselection()
       if len(i) > 0:
         i = i[0]
         filepaths = ast.literal_eval(self.listvar.get())
         p = filepaths[i]
         print(f'selecting {i} from {filepaths} which gives {p}')
         convert(p, f'{p}.pdf')
         print('done')

def main():
    a = App()
    a.run()

if __name__ == "__main__":
    main()