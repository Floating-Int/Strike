from node import Node
from math import floor, ceil


class Shape: # SimpleShape
    __slots__ = ("owner", "disabled", "width", "height")

    def __init__(self, owner: Node, width: int = 0, height: int = 0) -> None:
        self.owner = owner
        self.width = width
        self.height = height
        self.disabled = False

    def is_intersecting(self, shape) -> bool: # NOTE: only works with SimpleShape | support ReactiveShape
        if ceil(self.owner.x) >= floor(shape.owner.x):
            if ceil(self.owner.x) + self.width < floor(shape.owner.x) + shape.width:
                if ceil(self.owner.y) >= floor(shape.owner.y):
                    if ceil(self.owner.y) + self.height < floor(shape.owner.y) + shape.height:
                        return True
        return False


class ReactiveShape(Shape):
    __slots__ = ("disabled", "area")

    def __init__(self, owner: Node) -> None:
        self.owner = owner
        self.disabled = False

    def is_intersecting(self, shape) -> bool:
        return False


class Collider:
    _colliders = [] # may be an Area

    def __new__(cls, *args, **kwargs):
        instance = super().__new__(cls, *args, **kwargs)
        instance.shape = Shape(owner=instance)
        cls._colliders.append(instance)
        return instance
    
    def is_colliding_with(self, collider: Node) -> bool:
        return (not self.shape.disabled) and self.shape.is_intersecting(collider.shape)
    
    def get_colliders(self) -> list:
        colliders = []
        for collider in self._colliders:
            if collider.shape.disabled == True or collider == self:
                continue
            if self.is_colliding_with(collider):
                # collider._on_collision(self) # TODO: do from engine?
                colliders.append(collider)
        return colliders

    def collide_with(self, collider: Node) -> None:
        collider._on_collision(self)

    def _on_collision(self, collider: Node) -> None:
        return

    def free(self) -> None:
        self._colliders.remove(self)
        super().free()


class Area:
    _colliders = [] # may be an Area

    def __new__(cls, *args, **kwargs):
        instance = super().__new__(cls, *args, **kwargs)
        instance.shape = Shape(owner=instance)
        cls._colliders.append(instance)
        return instance
    
    def is_colliding_with(self, collider: Node) -> bool:
        return self.shape.is_intersecting(collider.shape)

    def get_colliders(self) -> list:
        colliders = []
        for collider in self._colliders:
            if collider == self or collider.shape.disabled == True:
                continue
            if self.is_colliding_with(collider):
                # collider._on_collision(self) # TODO: do from engine?
                colliders.append(collider)
        return colliders

    def collide_with(self, collider: Node) -> None:
        collider._on_collision(self)

    def _on_collision(self, collider: Node) -> None:
        return

    def free(self) -> None:
        self._colliders.remove(self)
        super().free()
