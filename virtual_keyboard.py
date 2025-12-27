import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ui_utils import LayoutManager

class OnScreenKeyboard(ttk.Frame):
    """
    Perfectly centered, fixed-grid on-screen keyboard
    6 rows x 10 columns — stable for tablet/touchscreens.
    """

    def __init__(self, parent, target_entry, close_callback, layout_manager=None):
        super().__init__(parent, bootstyle="dark")
        self.target = target_entry
        self.close_callback = close_callback
        self.lm = layout_manager
        self.caps = False

        # Scale padding if LM is available
        pad = self.lm.scaled(10) if self.lm else 10
        self.configure(padding=pad)

        # Configure Grid Weights so keys expand to fill width/height
        self.rows = 6
        self.cols = 10
        
        for r in range(self.rows):
            self.rowconfigure(r, weight=1)
        for c in range(self.cols):
            self.columnconfigure(c, weight=1)

        # Key layout (max 60 keys)
        self.keys = [
            "1","2","3","4","5","6","7","8","9","0",
            "q","w","e","r","t","y","u","i","o","p",
            "a","s","d","f","g","h","j","k","l","@",
            "z","x","c","v","b","n","m","#","(",")",
            "_","-",".",",","?","!","/","\\",":",";",
            "SPACE","CAPS","⌫","OK","+","=","'","\""
        ]


        self.render_keyboard()


    # -----------------------------------
    #           RENDER LAYOUT
    # -----------------------------------
    def render_keyboard(self):
        # Clear old
        for w in self.winfo_children():
            w.destroy()
            
        pad_val = self.lm.scaled(2) if self.lm else 2

        # Create fixed 6×10 grid
        idx = 0
        r = 0
        c = 0
        
        while idx < len(self.keys):
            key = self.keys[idx]
            display_key = key.upper() if (self.caps and key.isalpha()) else key
            
            # Determine colspan
            colspan = 1
            if key == "SPACE":
                colspan = 5
            
            # Create Widget
            if key == "":
                pass
            else:
                if key == "SPACE":
                    btn = ttk.Button(
                        self, text="SPACE", bootstyle=PRIMARY,
                        command=lambda: self.add_char(" ")
                    )
                elif key == "CAPS":
                    btn = ttk.Button(
                        self, text="CAPS", bootstyle=INFO,
                        command=self.toggle_caps
                    )
                elif key == "⌫":
                    btn = ttk.Button(
                        self, text="⌫", bootstyle=DANGER,
                        command=self.backspace
                    )
                elif key == "OK":
                    btn = ttk.Button(
                        self, text="OK", bootstyle=SUCCESS,
                        command=self.close_callback
                    )
                else:
                    btn = ttk.Button(
                        self, text=display_key, bootstyle=SECONDARY,
                        command=lambda ch=display_key: self.add_char(ch)
                    )
                
                # Use sticky "nsew" to make buttons fill the grid cell
                btn.grid(row=r, column=c, columnspan=colspan, padx=pad_val, pady=pad_val, sticky="nsew")

            # Advance
            c += colspan
            if c >= self.cols:
                c = 0
                r += 1
            
            idx += 1


    # -----------------------------------
    #         KEYBOARD FUNCTIONS
    # -----------------------------------
    def toggle_caps(self):
        self.caps = not self.caps
        self.render_keyboard()

    def add_char(self, char):
        self.target.insert(tk.END, char)

    def backspace(self):
        text = self.target.get()
        if text:
            self.target.delete(len(text)-1)
