from node import Node, Control
from item import Item
from interaction import Interactive
from ui import DecayLabel


class Slot:
    def __init__(self, item: Item, count: int = 1) -> None:
        self.item = item
        self.count = count


class Container:
    def __new__(cls: type, *args, **kwargs) -> type:
        instance = super().__new__(cls)
        instance.inventory = [] # fill with Slot instances
        return instance
    
    def add_item(self, item: Item, count: int = 1) -> None:
        # TODO: implement algorithm for adding items
        self.inventory.append(item) # FIXME


class Hotbar(Interactive, Container, DecayLabel):
    def __init__(self, owner=None, x: int = 0, y: int = 0, z: int = Control.TOP_LEVEL, text: str = None, decay: float = 1) -> None:
        super().__init__(owner, x, y, z, text, decay)
        self.precedence = 3
    
    def add_item(self, item: Item, count: int = 1) -> None:
        super().add_item(item, count)
        # self.text = f"┇{self.inventory[0].TEXTURE}┇" # DEV

    def is_available_for(self, interactor: Node) -> bool:
        return True # DEV

    def _on_interaction(self, interactor: Node, key: str = None) -> None:
        if key.isdigit():
            index = int(key) -1
            if index < len(self.inventory):
                self.text = f"┇{self.inventory[index].TEXTURE}┇"
                self.show()            


