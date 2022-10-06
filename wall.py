from node import Node
from structure import Structure
from collision import Collider


class Wall(Collider, Structure, Node):
    _TEXTURE = "#"

    def __init__(self, owner=None, x: int = 0, y: int = 0, z: int = 0, width: int = 1, height: int = 1) -> None:
        super().__init__(owner, x, y)
        self._width = width
        self._height = height
        self.shape.width = width
        self.shape.height = height
        self.content = [
            [self._TEXTURE] * width 
        ] * height

    @property
    def width(self) -> int:
        return self._width
    
    @width.setter
    def width(self, width: int) -> None:
        self._width = width
        self.content = [
            [self._TEXTURE] * width 
        ] * self._height

    @property
    def width(self) -> int:
        return self._width

    @property
    def height(self) -> int:
        return self._height
    
    @width.setter
    def height(self, height: int) -> None:
        self._height = height
        self.content = [
            [self._TEXTURE] * self._width 
        ] * height

    def _on_collision(self, collider: Node) -> None:
        # TODO: split up wall into smaller segments on hit
        # print("WALL HIT:", self)
        self.free()
