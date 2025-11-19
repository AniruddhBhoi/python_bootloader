import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *


class OnScreenKeyboard(ttk.Frame):
    """
    Perfectly centered, fixed-grid on-screen keyboard
    6 rows x 10 columns — stable for tablet/touchscreens.
    """

    def __init__(self, parent, target_entry, close_callback):
        super().__init__(parent, bootstyle="dark")
        self.target = target_entry
        self.close_callback = close_callback
        self.caps = False

        self.configure(padding=15)

        # fixed grid size
        self.rows = 6
        self.cols = 10

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

        # Create fixed 6×10 grid
        idx = 0
        for r in range(self.rows):
            for c in range(self.cols):
                if idx < len(self.keys):
                    key = self.keys[idx]
                else:
                    key = ""  # blank filler

                display_key = key.upper() if (self.caps and key.isalpha()) else key

                if key == "":
                    ttk.Label(self, text="", width=5).grid(row=r, column=c, padx=3, pady=3)
                elif key == "SPACE":
                    ttk.Button(
                        self, text="SPACE", bootstyle=PRIMARY, width=25,
                        command=lambda: self.add_char(" ")
                    ).grid(row=r, column=c, columnspan=5, padx=3, pady=3, sticky="ew")
                    # skip next columns
                    c += 4
                    idx += 1
                    continue
                elif key == "CAPS":
                    ttk.Button(
                        self, text="CAPS", bootstyle=INFO, width=8,
                        command=self.toggle_caps
                    ).grid(row=r, column=c, padx=3, pady=3)
                elif key == "⌫":
                    ttk.Button(
                        self, text="⌫", bootstyle=DANGER, width=8,
                        command=self.backspace
                    ).grid(row=r, column=c, padx=3, pady=3)
                elif key == "OK":
                    ttk.Button(
                        self, text="OK", bootstyle=SUCCESS, width=8,
                        command=self.close_callback
                    ).grid(row=r, column=c, padx=3, pady=3)
                else:
                    ttk.Button(
                        self, text=display_key, bootstyle=SECONDARY, width=5,
                        command=lambda ch=display_key: self.add_char(ch)
                    ).grid(row=r, column=c, padx=3, pady=3)

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
