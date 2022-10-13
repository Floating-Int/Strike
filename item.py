from node import Node
from interaction import Interactive


class Item(Interactive, Node):
    TEXTURE = "*"

    def __init__(self, owner: Node, offset: list = [0, 0]) -> None:
        super().__init__(owner)
        self.offset = offset
        self.active = False # DEV: set as True by default
        self.precedence = 10
        self.content = [list(self.TEXTURE)]
        self.visible = False # needs to manually be enabled # DEV
    
    def is_available_for(self, interactor: Node) -> bool:
        # return True
        return interactor.name == "Player" # DEV

    def _update(self, delta: float) -> None:
        # FIXME: offset
        self.position = self.owner.position
        self.x += self.offset[0]
        self.y += self.offset[1]
