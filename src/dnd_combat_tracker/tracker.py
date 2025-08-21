from typing import List, Optional
from dnd_combat_tracker.models import Creature

class CombatTracker:
    """
    a class to track d&d combat rounds and turns.
    this class :
        adds a creature,
        sorts creatures by their iniativee orders and tracks turns, and
        starts a turn.
    """

    def __init__(self):
        self.creatures: List[Creature] = []
        self.round = 0
        self.turn_index = -1

    def add_creature(self, creature: Creature):
        # add AND sort
        self.creatures.append(creature)
        self.creatures.sort(key=lambda c: c.initiative, reverse=True)

    def start(self):
        if not self.creatures:
            raise ValueError("there are no creatures in this combat!")
        self.round = 1
        self.turn_index = 0

    def next_turn(self) -> Creature:
        if self.turn_index == -1:
            self.start()
        self.turn_index = (self.turn_index + 1) % len(self.creatures)
        if self.turn_index == 0:
            self.round += 1
        return self.current

    @property
    def current(self) -> Optional[Creature]:
        # 
        if not self.creatures: # if no creatures
            return None
        if self.turn_index == -1: # if combat hasnt started
            return None
        return self.creatures[self.turn_index]

    @property
    def is_active(self) -> bool:
        return bool(self.creatures) and self.turn_index != -1
    