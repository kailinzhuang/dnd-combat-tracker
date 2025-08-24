import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
from datetime import datetime
from dnd_combat_tracker.tracker import CombatTracker
from dnd_combat_tracker.models import Creature

class CombatTrackerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("a d&d combat tracker !")
        self.root.geometry("1000x600")
        self.log = []
        self.edit_entry = None  # inline editor
        root.protocol("WM_DELETE_WINDOW", self.on_close)

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
        frm_sorted = ttk.LabelFrame(root, text="sorted by initiative        tip: double click to edit; command + select to deselect")
        frm_sorted.pack(fill="x", expand=True, padx=5, pady=5)

        self.tree_sorted = ttk.Treeview(frm_sorted, columns=("name", "init", "hp", "ac", "type"), show="headings", height=10)
        self.tree_sorted.heading("name", text="name")
        self.tree_sorted.heading("init", text="initiative")
        self.tree_sorted.heading("hp", text="HP")
        self.tree_sorted.heading("ac", text="AC")
        self.tree_sorted.heading("type", text="type")
        self.tree_sorted.pack(fill="both", expand=True)
        self.tree_sorted.bind("<Double-1>", self.on_double_click)  # double click to edit HP or AC

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
        ttk.Button(frm_ctrl, text="load csv", command=self.load_csv).pack(side="left", padx=5)
        ttk.Button(frm_ctrl, text="save csv", command=self.save_csv).pack(side="right", padx=5)
        ttk.Button(frm_ctrl, text="refresh", command=self.refresh).pack(side="left", padx=5)
        ttk.Button(frm_ctrl, text="start combat", command=self.start_combat).pack(side="left", padx=5)
        ttk.Button(frm_ctrl, text="next turn", command=self.next_turn).pack(side="left", padx=5)
        ttk.Button(frm_ctrl, text="quit", command=self.on_close).pack(side="right", padx=5)

    
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
        # clear view 
        for item in self.tree_sorted.get_children():
            self.tree_sorted.delete(item)

        # sort 
        sorted_creatures = sorted(self.tracker.creatures, key=lambda c: c.initiative, reverse=True)

        # show in tree view
        for c in sorted_creatures:
            type_text = "player" if c.is_player else "monster"
            self.tree_sorted.insert(
                "",
                "end",
                values=(c.name, c.initiative, c.hp, c.ac, type_text)
            )

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
            messagebox.showinfo("Success", f"Successfully saved: {filename}")
            
            if self.log:  # only if there is something in the log
                save_log = messagebox.askyesno("Save Log?", "Would you also like to save the combat log?")
                if save_log:
                    self.save_log()

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
        # make sure there is a combat happening.
        if not self.tracker.is_active:
            messagebox.showerror("Error", "there is no active combat! please start a combat first.")
            return
        
        try:
            creature = self.tracker.next_turn()
        except ValueError as e:
            messagebox.showerror("Error", str(e))
            return

        if creature is None:
            self.lbl_current.config(text="no creature")
            return

        # update label with round info
        self.lbl_current.config(
            #assuming only hp changes... might add a toggle later to select what to show?
            text=f"Round {self.tracker.round}: current turn: {creature.name} (HP {creature.hp})" 
        )
        self.add_log(f"{creature.name}'s turn started (HP {creature.hp})")

        # clear highlights and selections
        for item in self.tree_sorted.get_children():
            self.tree_sorted.item(item, tags=())
        self.tree_sorted.selection_remove(self.tree_sorted.selection())

        # destroy inline editor if open
        if self.edit_entry:
            self.edit_entry.destroy()
            self.edit_entry = None

        # highlight current creature
        self._highlight_current_creature(creature)

    def _highlight_current_creature(self, creature):
        """highlight the current creature in the initiative table"""
        for child in self.tree_sorted.get_children():
            if self.tree_sorted.item(child)['values'][0] == creature.name:
                if creature.is_player:
                    self.tree_sorted.item(child, tags=("highlight_player",))
                else:
                    self.tree_sorted.item(child, tags=("highlight_monster",))
                break
    
    def on_double_click(self, event):
        """
        this allows editing HP or AC on double-click.
        """

        row_id = self.tree_sorted.identify_row(event.y)
        col_id = self.tree_sorted.identify_column(event.x)

        if not row_id or not col_id:
            return

        # focus on the double clocked row and column
        self.tree_sorted.selection_set(row_id)
        self.tree_sorted.focus(row_id)

        # 0 = name, 1 = init, 2 = hp, 3 = ac, 4 = type)
        col_index = int(col_id.replace("#", "")) - 1  

        if col_index not in (2, 3, 4):
            return

        x, y, width, height = self.tree_sorted.bbox(row_id, col_id)
        old_value = self.tree_sorted.item(row_id, "values")[col_index]

        if self.edit_entry:
            self.edit_entry.destroy()
            self.edit_entry = None

        if col_index == 4:  
            # type 
            entry = ttk.Combobox(self.tree_sorted, values=["player", "monster"], state="readonly")
            entry.place(x=x, y=y, width=width, height=height)
            entry.set(old_value)
            entry.focus()
            self.edit_entry = entry
        else: 
            # HP or AC
            entry = tk.Entry(self.tree_sorted)
            entry.place(x=x, y=y, width=width, height=height)
            entry.insert(0, old_value)
            entry.focus()
            self.edit_entry = entry

        def save_edit(event=None):
            new_value = entry.get().strip()
            values = list(self.tree_sorted.item(row_id, "values"))
            name = values[0]

            # update creature
            for c in self.tracker.creatures:
                if c.name == name:
                    if col_index == 2:  # HP
                        if not new_value.isdigit():
                            messagebox.showerror("Invalid value", "HP must be a number.")
                            return
                        c.hp = int(new_value)
                    elif col_index == 3:  # AC
                        if not new_value.isdigit():
                            messagebox.showerror("Invalid value", "AC must be a number.")
                            return
                        c.ac = int(new_value)
                    break

            # then update table
            values[col_index] = new_value
            self.tree_sorted.item(row_id, values=values)

            entry.destroy()
            self.edit_entry = None

        # if press enter or click outside, save the edit
        entry.bind("<Return>", save_edit)
        entry.bind("<FocusOut>", save_edit)


    def add_log(self, text):
        """add a timestamped entry to the combat log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        round_info = f"Round {self.tracker.round}" if hasattr(self.tracker, "round") else ""
        self.log.append(f"[{timestamp}] {round_info} — {text}")
    
    def save_log(self):
        """
        save combat log to a csv file.
        """
        if not self.log:
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv", filetypes=[("CSV files", "*.csv")], title="Save Combat Log"
        )
        if not filename:
            return
        
        try:
            with open(filename, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["timestamped_event"])
                for entry in self.log:
                    writer.writerow([entry])
            messagebox.showinfo("Success", f"Combat log saved to {filename}")
        except Exception as e:
            messagebox.showerror("Error saving log", str(e))
    
    def on_close(self):
        if self.log:
            if messagebox.askyesno("Quit", "There is a combat log.\nWould you like to save it before quitting?"):
                self.save_log()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = CombatTrackerGUI(root)
    root.mainloop()