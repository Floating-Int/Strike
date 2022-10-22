from node import Node
from interaction import Interactive
from container import Container


class Depot(Interactive, Container, Node):

    def __init__(self, owner: Node = None, x: int = 0, y: int = 0, z: int = 0) -> None:
        super().__init__(owner, x, y, z)
        self.content = [list("{=}")]
        self._effect_duration = 1.5 # seconds
        self._elapsed_time = self._effect_duration
    
    def _update(self, delta: float) -> None:
        if self._elapsed_time >= self._effect_duration:
            self.content = [list("{=}")]
            return
        self.content = [list("{ }")]
        self._elapsed_time += delta

    def _on_interaction(self, interactor: Node, key: str = None) -> None:
        if key == "interact":
            if interactor.name == "Player":
                interactor.has_shell = True
                # visual effect
                self.content = [list("{ }")]
                self._elapsed_time = 0
