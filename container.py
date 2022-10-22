from node import Node, Control
from item import Item
from interaction import Interactive
from event import InputHandler, InputEvent
from ui import DecayLabel


class Container:
    inventory: list = []

    def add_item(self, item: Item) -> None:
        self.inventory.append(item)
        item.active = False
        item.visible = False


class Hotbar(InputHandler, Container, DecayLabel): # TODO: move to other file. Container should be alone because it's a component
    SPACE = "."
    # TOP = "┏━┓"
    # SIDE_LEFT = "┃"
    # SIDE_RIGHT = "┃"
    # BOTTOM = "┗━┛"
    # SEPARATOR = "┣━┫"
    TOP = "┌─┐"
    SIDE_LEFT = "│"
    SIDE_RIGHT = "│"
    BOTTOM = "└─┘"
    SEPARATOR = "├─┤"  
    active = "┃"
    passive = "."

    def __init__(self, owner=None, x: int = 0, y: int = 0, z: int = Control.TOP_LEVEL, text: str = None, decay: float = 1) -> None:
        super().__init__(owner, x, y, z, text, decay)
        self.add_action("cycle_next", key="tab")
        self.add_action("slot_1", key="1")
        self.add_action("slot_2", key="2")
        self.add_action("slot_3", key="3")
        self._index = 0

    def add_item(self, item: Item) -> None:
        super().add_item(item)
        if len(self.inventory) == 1: # was first element added
            self._index = 0
            item.active = True

    def _input(self, event: InputEvent) -> None:
        if event.pressed:
            if event.action == "slot_1":
                self._index = 0
            elif event.action == "slot_2":
                self._index = 1
            elif event.action == "slot_3":
                self._index = 2
            # TODO: add more slots
            else:
                return # returns if not slot key pressed
            self._index = min(self._index, len(self.inventory) -1) # clamp index
            # construct visual part
            self.content = []
            self.content.append(list(self.SPACE * len(self.passive) + self.TOP))
            last_index = len(self.inventory) -1
            for idx, item in enumerate(self.inventory):
                if idx == self._index:
                    line = list(f"{self.active}{self.SIDE_LEFT}{item.TEXTURE}{self.SIDE_RIGHT}")
                else:
                    line = list(f"{self.passive}{self.SIDE_LEFT}{item.TEXTURE}{self.SIDE_RIGHT}")
                self.content.append(line)
                if not idx == last_index:
                    self.content.append(list(self.SPACE * len(self.passive) + self.SEPARATOR))
            self.content.append(list(self.SPACE * len(self.passive) + self.BOTTOM))
            self.show()


