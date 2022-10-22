from node import Node


class Item(Node):
    TEXTURE = "*" # placeholder

    def __init__(self, owner: Node, offset: list = [0, 0]) -> None:
        super().__init__(owner)
        self.offset = offset
        self.active = True
        self.content = [list(self.TEXTURE)]
        self.visible = False
    
    def _update(self, delta: float) -> None:
        self.position = self.owner.position
        self.x += self.offset[0]
        self.y += self.offset[1]
