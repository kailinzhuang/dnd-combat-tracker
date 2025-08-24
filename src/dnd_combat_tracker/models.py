from dataclasses import dataclass

@dataclass
class Creature:
    name: str
    hp: int
    ac: int
    initiative: int
    is_player: bool = False