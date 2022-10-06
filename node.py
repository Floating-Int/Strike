from typing import Any
from functools import wraps


class Node:
    root = None
    _nodes = []
    _uid = 0 # unique Node id

    def __new__(cls, *args, **kwargs):
        instance = super().__new__(cls)
        cls._nodes.append(instance)
        # generate new unique ID
        instance._uid = cls._uid # NOTE: DO NOT CHANGE AT RUNTIME!
        cls._uid += 1
        # add required attributes
        instance.owner = None
        instance.name = cls.__name__
        instance.x = 0
        instance.y = 0
        instance.z = 0
        instance.visible = True
        instance.content = [] # 2D array: [["l", "1"], ["l", "2"]]
        return instance

    def __init__(self, owner=None, x: int = 0, y: int = 0, z: int = 0) -> None:
        """Init base class node

        Args:
            owner (Node, optional): owner of this node. Defaults to None.
            x (int, optional): x position. Defaults to 0.
            y (int, optional): y position. Defaults to 0.
            z (int, optional): z index. Defaults to 0.
        """
        self.owner = owner
        self.x = x
        self.y = y
        self.z = z
    
    @classmethod # @override
    def from_request(cls, args: list, kwargs: dict): # -> Instance
        """Returns a modified instance based on the creation request

        Args:
            args (list): _description_
            kwargs (dict): _description_

        Returns:
            _type_: _description_
        """
        return cls(*args, **kwargs)
    
    @property
    def position(self) -> tuple:
        return [self.x, self.y]
    
    @position.setter
    def position(self, position: list) -> None:
        self.x, self.y = position

    def _render(self) -> list:
        return self.content
    
    def _update(self, delta: float) -> None:
        return
    
    def free(self) -> None:
        """Delete Node object"""
        self.owner = None
        self._nodes.remove(self)


class Control:
    """Usage: class ExampleUI(Control, Node): ...
    """
    TOP_LEVEL = 100 # default z-index for control nodes

    def __init__(self, owner=None, x: int = 0, y: int = 0, z: int = TOP_LEVEL) -> None:
        super().__init__(owner, x, y, z)
        self._initial_x = x
        self._initial_y = y

    def __new__(cls, *args, **kwargs):
        instance = super().__new__(cls)
        instance._update = cls._update_wrapper(instance._update)
        return instance
    
    def _update_wrapper(fn): # 'fn' is '_update'
        self = fn.__self__
        @wraps(fn)
        def _update(delta):
            fn(delta)
            # do position calculations
            camera = self.root.get_current_camera() # NOTE: camera is not centered
            self.x = camera.x + self._initial_x
            self.y = camera.y + self._initial_y
            # self.x = self.owner.x + self._initial_x - sum(divmod(self.root.width, 2))
            # self.y = self.owner.y + self._initial_y - sum(divmod(self.root.height, 2))
        return _update


# class HollowNode(Node):
#     _REQUEST_ATTR_CHANGED = "ATTR:{}{}$" # name, value
#     def __setattr__(self, name: str, value: Any) -> None:
#         self.__dict__[name] = value
#         self.root.send(self._REQUEST_ATTR_CHANGED)