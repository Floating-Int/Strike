from nodes import *
from interaction import Interactive, Interactor
from item import Item
import math


class Wrench(Item):
    TEXTURE = "‡"
    _REQUEST_CREATE = "CREATE:{structure}:{x}:{y}"
    _ROTATIONS = [
        (1, 0),
        (0, 1),
        (-1, 0),
        (0, -1)
    ]
    _ROTATION_SYMBOLS = ["⇒", "⇓", "⇐", "⇑"] # points from origin
    structures = ["Wall", "Mortar", "Flak"] # TODO: add setter for this (update longest length in item label)
    key_next = "tab"
    key_rotate = "r"
    key_build = "q"

    def __init__(self, owner: Node, offset: list = [0, 0]) -> None:
        super().__init__(owner, offset)
        self.precedence = 5
        self._index = 0
        self._longest_len = len(max(self.structures, key=len))
        self._item_label = ItemLabel(self, y=sum(divmod(self.root.height, 3)), decay=2.0, width=self._longest_len)
        self._rotation_index = 0 # ranges from 0-3 | TODO: increase to 8?
        self._rotation_index_ui = DecayLabel(self, y=self.root.height // 2, decay=1.0)
    
    def _on_interaction(self, interactor: Node, key: str = None) -> None:
        if key == self.key_next:
            self._index = (self._index +1) % len(self.structures)
            self._item_label.text = self.structures[self._index]
            self._item_label.show()
        elif key == self.key_rotate:
            self._rotation_index = (self._rotation_index + 1) % 4 # ranges from 0-3
            symbol = self._ROTATION_SYMBOLS[self._rotation_index]
            self._rotation_index_ui.text = f"[Direction: ({symbol})]"
            self._rotation_index_ui.show()
        elif key == self.key_build:
            Struct = globals()[self.structures[self._index]]
            if self.root.resource_system.resources >= Struct.COST:
                self.root.resource_system.resources -= Struct.COST
                a, b = self._ROTATIONS[self._rotation_index]
                x = int(self.owner.x + a)
                y = int(self.owner.y + b)
                instance = Struct(x=x, y=y) # create unrefed node
                # check if space is not taken
                # if instance.get_colliders():
                #     self.root.resource_system.resources += Struct.COST
                #     instance.free()
                #     return
                self.root.send(self._REQUEST_CREATE.format(structure=Struct.__name__, x=x, y=y))


class RemoteTrigger(Interactor, Item, Node):
    TEXTURE = "±"

    def __init__(self, owner: Node, offset: list = [0, 0]) -> None:
        super().__init__(owner, offset)
        self.precedence = 5
        self._links = [] # node refs
        self._target = None
    
    def link_with(self, interactive: Interactive) -> None:
        self._links.append(interactive)

    def clear_links(self) -> None:
        self._links = []

    def _on_interaction(self, interactor: Node, key: str = None) -> None:
        if key == "f": # link with mortar
            interactive = self.get_available_interactive()
            if interactive:
                if interactive.name in ["Mortar", "Flak"]:
                    self.link_with(interactive)
                    # print("LINK:", interactive.name)
        elif key == "e_released":
            self._target = interactor.marker.position
            # print("TARGET:", interactor.marker.position)
        elif key == "space":
            for linked in self._links:
                linked.set_target(self._target) # NOTE: have to be either Mortar or Flak | add tags?
                self.interact_with(linked, key=key)

    def free(self) -> None:
        self._linked = None
        super().free()


class Bullet(Collider, Node):
    # TODO: change to Area instead of Collider
    _SPEED = 32 # TODO: use RayCast instead of collider | combine with collider?
    _SYMBOLS = ["|", "\\", "―", "/", "|", "\\", "―", "/"]

    def __init__(self, owner=None, x: int = 0, y: int = 0, z: int = 0, direction: list = None) -> None:
        super().__init__(owner, x, y, z)
        self.shape.width = 1
        self.shape.height = 1
        self._motion = [0, 0]
        a, b = direction
        length = math.sqrt(a*a + b*b)
        if a != 0:
            self._motion[0] = a / length
        if b != 0:
            self._motion[0] = b / length
        radians = math.atan2(a, b)
        normalized = (radians / math.pi)
        if normalized == 0:
            symbol = self._SYMBOLS[0]
        else:
            idx = int(round(normalized * 4))
            symbol = self._SYMBOLS[idx]
        self.content = [[symbol]]
    
    def _update(self, delta: float) -> None:
        self.x += self._motion[0] * self._SPEED * delta
        self.y += self._motion[1] * self._SPEED * delta
        for collider in self.get_colliders():
            if collider.name == "Player":
                collider.health -= 1
            self.free()
            break


class Firearm(Item, Node):
    _PROJECTILE = Bullet

    def __init__(self, owner: Node, offset: list = [0, 0]) -> None:
        super().__init__(owner, offset)
        self._last_direction = [1, 0]

    def _update(self, _delta: float) -> None:
        if self.owner.direction != [0, 0]:
            self._last_direction = self.owner.direction
        elif self.owner.direction[0] != 0:
            self._last_direction[0] = self.owner.direction[0]
        elif self.owner.direction[1] != 0:
            self._last_direction[1] = self.owner.direction[1]
        if self.owner.direction[0] != 0 or self.owner.direction[1] != 0:
            # print("FIREARM:", self._last_direction)
            ...
        self._last_direction = self.owner.direction
    
    def _on_interaction(self, interactor: Node, key: str = None) -> None:
        if key == "space":
            # create unrefed node
            x = interactor.x + self._last_direction[0]
            y = interactor.y + self._last_direction[1]
            # print("BULLET:", self._last_direction)
            # print(self._last_direction)
            instance = self._PROJECTILE(self, x=x, y=y, direction=self._last_direction)

