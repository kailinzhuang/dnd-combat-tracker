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
        self.edit_entry = None  # inline editor

        self.tracker = CombatTracker() 

        # ========== add a new creature: name, initiative, type ==========
        frm_input = ttk.LabelFrame(root, text="add a creature")
        frm_input.pack(fill="x", padx=10, pady=10)

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
        ttk.Button(frm_input, text="add", command=self.add_creature).grid(row=0, column=11, padx=5)

        # ========== initiative order table ==========
        frm_sorted = ttk.LabelFrame(root, text="sorted by initiative")
        frm_sorted.pack(fill="x", expand=True, padx=10, pady=10)

        self.tree_sorted = ttk.Treeview(frm_sorted, columns=("name", "init", "hp", "ac", "type"), show="headings", height=10)
        self.tree_sorted.heading("name", text="name")
        self.tree_sorted.heading("init", text="initiative")
        self.tree_sorted.heading("hp", text="HP")
        self.tree_sorted.heading("ac", text="AC")
        self.tree_sorted.heading("type", text="type")
        self.tree_sorted.pack(fill="both", expand=True)

        # ========== current turn ==========
        frm_current = ttk.LabelFrame(root, text="current turn")
        frm_current.pack(fill="x", padx=10, pady=5)
        self.lbl_current = ttk.Label(frm_current, text="no active combat / turn!")
        self.lbl_current.pack(padx=5, pady=5)
        self.tree_sorted.tag_configure("highlight_player", background="lightblue")
        self.tree_sorted.tag_configure("highlight_monster", background="purple")

        # =========== control buttons ==========
        frm_ctrl = ttk.Frame(root)
        frm_ctrl.pack(fill="x", padx=10, pady=10)
        ttk.Button(frm_ctrl, text="load csv", command=self.load_csv).pack(side="top", padx=5)
        ttk.Button(frm_ctrl, text="save csv", command=self.save_csv).pack(side="right", padx=5)
        ttk.Button(frm_ctrl, text="refresh", command=self.refresh).pack(side="left", padx=5)
        ttk.Button(frm_ctrl, text="start combat", command=self.start_combat).pack(side="left", padx=5)
        ttk.Button(frm_ctrl, text="next turn", command=self.next_turn).pack(side="left", padx=5)
        ttk.Button(frm_ctrl, text="quit", command=root.destroy).pack(side="right", padx=5)

    
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
    
    def refresh(self):
        pass

    def load_csv(self):
        filename = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if not filename:
            return
        try:
            self.tracker.creatures.clear() # clear the current list. not sure if this is necessary/desired.

            with open(filename, newline="") as f:
                reader = csv.DictReader(f)

                # for each row in the CSV, create a `Creature` object and add it
                for row in reader:
                    creature = Creature(
                        name=row["name"],
                        initiative=int(row["initiative"]),
                        is_player=row["is_player"].lower() in ("true", "1", "yes"),
                        hp=int(row.get("hp", 0)),
                        ac=int(row.get("ac", 0)) # default to 0. may need to add a check later before combat.
                    )
                    self.tracker.add_creature(creature)
            self.refresh()
        except Exception as e:
            messagebox.showerror("Error loading CSV", str(e))

    def save_csv(self):
        filename = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if not filename:
            return
        try:
            with open(filename, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["name", "initiative", "is_player", "hp", "ac"])
                for c in self.tracker.creatures:
                    writer.writerow([c.name, c.initiative, c.is_player, c.hp, c.ac])
            messagebox.showinfo(f"successfully saved: {filename}")
        except Exception as e:
            messagebox.showerror("Error saving CSV", str(e))

    def start_combat(self):
        
        # when a new combat is started, starting a fresh log (i.e., round, and turn info)
        confirm = messagebox.askyesno(
            "Start Combat!",
            "Starting a new combat... \nreset Round = 1, Turn = 1.\n\nDo you wish to continue?"
        )
        if not confirm:
            return

        try:
            self.tracker.start()
        except ValueError as e:
            messagebox.showerror("Error", str(e))
            return

        self.add_log("Combat started.")

        # show the first creature
        creature = self.tracker.current
        self.lbl_current.config(
            text=f"Round {self.tracker.round}, current turn: {creature.name})"
        )
        

    def next_turn(self):
        pass

if __name__ == "__main__":
    root = tk.Tk()
    app = CombatTrackerGUI(root)
    root.mainloop()