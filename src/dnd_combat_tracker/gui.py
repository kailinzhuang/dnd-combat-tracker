import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
from .tracker import CombatTracker

from dataclasses import dataclass

@dataclass
class Creature:
    name: str
    hp: int
    ac: int
    initiative: int
    is_player: bool = False


class CombatTrackerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("a d&d combat tracker !")
        self.root.geometry("1000x600")
        self.log = []

        self.tracker = CombatTracker() 

        # ========== add a new creature: name, initiative, type ==========
        frm_input = ttk.LabelFrame(root, text="add a creature")
        frm_input.pack(fill="x", padx=20, pady=20)

        ttk.Label(frm_input, text="name:").grid(row=0, column=0, padx=5, pady=5)
        self.name_var = tk.StringVar()
        ttk.Entry(frm_input, textvariable=self.name_var, width=8).grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frm_input, text="initiative:").grid(row=0, column=2, padx=5, pady=5)
        self.init_var = tk.StringVar()
        ttk.Entry(frm_input, textvariable=self.init_var, width=4).grid(row=0, column=3, padx=5, pady=5)

        self.category_var = tk.StringVar(value="player")
        ttk.Radiobutton(frm_input, text="player", variable=self.category_var, value="player").grid(row=0, column=4)
        ttk.Radiobutton(frm_input, text="monster", variable=self.category_var, value="monster").grid(row=0, column=5)

        ttk.Label(frm_input, text="AC:").grid(row=0, column=5, padx=5, pady=5)
        self.ac_var = tk.IntVar()  
        ttk.Entry(frm_input, textvariable=self.ac_var, width=4).grid(row=0, column=6, padx=5, pady=5)

        ttk.Label(frm_input, text="HP:").grid(row=0, column=7, padx=5, pady=5)
        self.hp_var = tk.IntVar()
        ttk.Entry(frm_input, textvariable=self.hp_var, width=4).grid(row=0, column=8, padx=5, pady=5)
    

if __name__ == "__main__":
    root = tk.Tk()
    app = CombatTrackerGUI(root)
    root.mainloop()