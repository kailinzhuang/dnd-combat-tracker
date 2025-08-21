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

        ttk.Label(frm_input, text="AC:").grid(row=0, column=4, padx=5, pady=5)
        self.ac_var = tk.IntVar()  
        ttk.Entry(frm_input, textvariable=self.ac_var, width=4).grid(row=0, column=5, padx=5, pady=5)

        ttk.Label(frm_input, text="HP:").grid(row=0, column=6, padx=5, pady=5)
        self.hp_var = tk.IntVar()
        ttk.Entry(frm_input, textvariable=self.hp_var, width=4).grid(row=0, column=7, padx=5, pady=5)

        ttk.Label(frm_input, text="type:").grid(row=0, column=8, padx=5, pady=5)
        self.category_var = tk.StringVar(value="player")
        ttk.Radiobutton(frm_input, text="player", variable=self.category_var, value="player").grid(row=0, column=9)
        ttk.Radiobutton(frm_input, text="monster", variable=self.category_var, value="monster").grid(row=0, column=10)

        # add button to add a new creature.
        ttk.Button(frm_input, text="add", command=self.add_creature).grid(row=0, column=9, padx=5)

    def add_creature(self):
        try:
            name = self.name_var.get().strip()
            init = int(self.init_var.get())
            ac = self.ac_var.get()
            hp = self.hp_var.get()

            # must have a name. the rest can be empty... -> might make this a required field later.
            if not name:
                raise ValueError("name is empty.")
            
            # also should have an init value so it can be sorted later.
            if not init:
                raise ValueError("initiative is empty.")
            
        except ValueError as e:
            messagebox.showerror("invalid input", str(e))
            return

        is_player = self.category_var.get() == "player"
        new_creature = Creature(name=name, ac=ac, hp=hp, initiative=init, is_player=is_player)
        self.tracker.add_creature(new_creature)

        # clear the input fields once the new creature has been added.
        self.name_var.set("")
        self.init_var.set("")
        self.refresh()
    

if __name__ == "__main__":
    root = tk.Tk()
    app = CombatTrackerGUI(root)
    root.mainloop()