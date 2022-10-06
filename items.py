from nodes import *
from item import Item


class Wrench(Item):
    structures = ["Wall", "Mortar", "Flak"] # TODO: add setter for this (update longest length in item label)

    def __init__(self, owner: Node, offset: list = [0, 0]) -> None:
        super().__init__(owner, offset)
        self.index = 0
        self.precedence = 5
        self._longest_len = len(max(self.structures, key=len))
        self._item_label = ItemLabel(self, y=5, width=self._longest_len)

    def _on_interaction(self, interactor: Node, key: str = None) -> None:
        if key.isdigit():
            index = float(key) -1
            if index <= len(self.structures):
                self.index = int(index)
                self._item_label.text = self.structures[self.index]
                self._item_label.show()
        elif key == "q": # build
            Struct = globals()[self.structures[self.index]]
            if self.root.resource_system.resources >= Struct.COST:
                self.root.resource_system.resources -= Struct.COST
                x = self.owner.x - self.owner.direction[0]
                y = self.owner.y - self.owner.direction[1]
                instance = Struct(x=x, y=y)
