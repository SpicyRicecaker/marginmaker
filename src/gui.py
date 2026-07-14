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

class App():
    def __init__(self):
      self.margin = 500

      self.root = TkinterDnD.Tk()  # Notice - use this instead of tk.Tk()
      # self.root.geometry("500x400")
      self.root.title("Margin X-Spandr+🍎🍎🍎🍎🍎")

      self.margin_str = StringVar(self.root)

      frm0 = ttk.Frame(self.root, padding=10)
      frm0.pack()

      frm = ttk.Frame(frm0, padding=10)
      frm.grid()

      # BIGDESCRIPTION = ttk.Label(frm, text="HAVE YOU EVER WANTED TO CONVERT YOUR PDFS? WELL NOW INTRODUCING ooops caps MARGIN X-SPANDR+!" \
      # "NOW YOU CAN SPEAK BACK AGAINST THESE TEXTBOOK AUTHORS" \
      # "EXPRESS YOUR OPINION" \
      # "AND REACH YOUR OWN CONCLUSIONS" \
      # "NOW ONLY FREE")
      # BIGDESCRIPTION.grid(column=0, row=2)

      label1 = ttk.Label(frm, text="Drop file here!")
      label1.grid(column=1, row=0)

      self.listvar = StringVar()

      self.dropbox = tk.Listbox(frm, width=30, height=20, listvariable=self.listvar)
      def on_change(*args):
        print(self.listvar.get())
      
      # In Python, trace_add takes (mode, callback) and callback receives standard args (*args)
      self.listvar.trace_add("write", on_change)
      self.dropbox.grid(column=1, row=1)

      def on_drop(event):
          # event.data is a raw Tcl list string, not a Python list
          for path in self.root.tk.splitlist(event.data):
              self.dropbox.insert(tk.END, path)

      self.dropbox.drop_target_register(DND_FILES)
      self.dropbox.dnd_bind("<<Drop>>", on_drop)

      instafocus(self.root)
      
      cv = ttk.Button(frm, text="Convert selected pdf", command=self.on_mousedown)
      cv.grid(column=0, row=1)

      # mg = ttk.Label(frm, text="Margin sides")
      # mg.grid(column=1, row=1)

      frm2 = ttk.Frame(frm, padding=0)
      frm2.grid(column=0, row=0)

      mg = ttk.Label(frm2, text="Margin sides")
      mg.grid(column=0, row=0)

      mg_txt = ttk.Entry(frm2, textvariable=self.margin_str)
      mg_txt.grid(column=0, row=1)
      mg_txt.insert(0, "500")

      def on_change(*args):
          print(self.margin_str.get())

      # In Python, trace_add takes (mode, callback) and callback receives standard args (*args)
      self.margin_str.trace_add("write", on_change)


    def run(self):
        self.root.mainloop()

    def on_mousedown(self):
       print('hiiiiiiiiiiiiiiiiiiiiiiiii')
       # non_numeric = False
       # for c in '0123456789'.split(''):
       self.margin = int(self.margin_str.get())

       i = self.dropbox.curselection()
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