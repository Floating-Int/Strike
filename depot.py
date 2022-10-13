from node import Node
from interaction import Interactive
from container import Container
from nodes import Shell, FlakShell


class Depot(Interactive, Container, Node):

    def __init__(self, owner=None, x: int = 0, y: int = 0, z: int = 0) -> None:
        super().__init__(owner, x, y, z)
        self.content = [list("{=}")]
        self.inventory = {"GenericShell": float("inf")}

    def _on_interaction(self, interactor: Node, key: str = None) -> None:
        if not isinstance(interactor, Container): # TODO: add system for type checking, so it can accept string
            return
        if key == "f":
            if not self.current in interactor.inventory:
                interactor.inventory["GenericShell"] = 0
            interactor.inventory["GenericShell"] += 1
