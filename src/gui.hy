(import tkinter :as tk)
(import tkinter.ttk [Frame Label Button]) ; Optional based on commented imports
(import tkinter.ttk :as ttk)
(import tkinterdnd2 [DND_FILES TkinterDnD])

(defn instafocus [window]
  ;; 1. Force the window to the very top layer
  (.attributes window "-topmost" True)
  
  ;; 2. Lift it above everything else
  (.lift window)
  
  ;; 3. Forcefully grab system focus 
  ;; (.focus-force window)
  
  ;; 4. Release the "always on top" behavior after an idle cycle, 
  ;; so the user can still put other windows over it if they want.
  (.after_idle window window.attributes "-topmost" False))

(defn init_gui []
  (setv root (TkinterDnD.Tk)) ; notice - use this instead of tk.Tk()
  (.geometry root "400x300")

  (let [frm0 (ttk.Frame root :padding 10)]
    (.pack frm0)

    (let [frm (ttk.Frame frm0 :padding 10)]
      (.grid frm)

      (.grid (ttk.Label frm :text "Drop file here!") :column 0 :row 0)

      (let [lb (tk.Listbox frm :width 30 :height 20)]
        (.grid lb :column 0 :row 1)
        (defn on-drop [event]
          ;; event.data is a raw Tcl list string, not a Python list
          (for [path (.splitlist root.tk event.data)]
            (.insert lb tk.END path)))
        (.drop-target-register lb DND_FILES)
        (.dnd-bind lb "<<Drop>>" on-drop)

        (instafocus root)
        
        root)
      ))
  )

(defn main []
  (setv root (init_gui))
  (.mainloop root))

(when (= __name__ "__main__") (main))