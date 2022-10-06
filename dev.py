from node import Node


class H2O(Node):
    def __init__(self, owner=None, x: int = 0, y: int = 0, z: int = 0) -> None:
        super().__init__(owner, x, y, z)
        self.content = [
            list("  O  "),
            list(" / \\ "),
            list("H   H"),
        ]