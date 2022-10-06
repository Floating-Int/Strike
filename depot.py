from node import Node
from interaction import Interactive
from mortar import Shell


class Depot(Interactive, Node):

    def __init__(self, owner=None, x: int = 0, y: int = 0, z: int = 0) -> None:
        super().__init__(owner, x, y, z)
        self.content = [
            list("{=}")
        ]
        self.inventory = {""}

    def is_available_for(self, interactor) -> bool:
        if interactor.x >= self.x and interactor.x < self.x + 3:
            if interactor.y >= self.y and interactor.y < self.y + 1:
                return True
        return False
    
    def _on_interaction(self, interactor, key: str = None) -> None:
        ...
