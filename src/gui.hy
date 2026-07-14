(import tkinter :as tk)
(import tkinter [Entry StringVar])
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
  (setv margin-str StringVar)

  (setv root (TkinterDnD.Tk)) ; notice - use this instead of tk.Tk()
  (.geometry root "500x400")

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

        (instafocus root))
      
      (let [cv (ttk.Button frm :text "Convert selected pdf")]
        (.grid cv :column 1 :row 0))

      ; (let [mg (ttk.Label frm :text "Margin sides")]
      ;   (.grid mg :column 1 :row 1)
      ;   )
      (let [frm2 (ttk.Frame frm :padding 0)]
        (.grid frm2 :column 1 :row 1)

        (let [mg (ttk.Label frm2 :text "Margin sides")]
          (.grid mg :column 0 :row 0)
          )

        (let [mg-txt (ttk.Entry frm2 :textvariable margin-str)]
           (.grid mg-txt :column 0 :row 1)
           (.insert mg-txt 0 "500")

           (defn on-change [e]
             (print margin-str))

           (.trace-add margin-str margin-str on-change "write")
          )
          )
      root
      ))
  )

(defn main []
  (setv root (init_gui))
  (.mainloop root))

(when (= __name__ "__main__") (main))