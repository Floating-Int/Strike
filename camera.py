from node import Node


class Camera(Node): # TODO: make view rect
    current = Node()

    @classmethod
    def set_current(cls, camera: Node) -> None:
        cls.current = camera
    
    @classmethod
    def get_current(cls) -> Node:
        return cls.current
    
    def __init__(self, owner=None, x: int = 0, y: int = 0) -> None:
        super().__init__(owner, x, y)
        
