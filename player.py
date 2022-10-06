from node import Node
from interaction import Interactor
from collision import Collider
from networking import Informative
from camera import Camera
from ui import HealthBar, Compass, NodeCounter
import keyboard


class Marker(Node):
    _SPEED = 16

    def __init__(self, owner=None, x: int = 0, y: int = 0, z: int = 0) -> None:
        super().__init__(owner, x, y, z)
        self.content = [["O"]]
        self.notify = ["x", "y"]
        self.is_moving = False

    def _update(self, delta: float) -> None:
        if self.is_moving:
            current = (self.x, self.y)
            if keyboard.is_pressed("d"):
                self.x += self._SPEED * delta
            if keyboard.is_pressed("a"):
                self.x -= self._SPEED * delta
            if keyboard.is_pressed("w"):
                self.y -= self._SPEED * delta
            if keyboard.is_pressed("s"):
                self.y += self._SPEED * delta
            if (self.x, self.y) != current: # moved
                self.root.send("ATTR:x={x}:y={y}".format(x=self.x, y=self.y))


class Player(Interactor, Collider, Node):
    _SPEED = 16 # TODO: fix issue when speed is decimal using floor and ceil

    def __init__(self, owner: Node = None, x: int = 0, y: int = 0, z: int = 0) -> None:
        super().__init__(owner, x, y, z)
        self.content = [["@"]]
        self.notify = ["position"]
        self.target = None # 2D point
        self.direction = [0, 0]
        self._is_moving = True
        self._marker = Marker(self, z=2)
        self._marker.visible = False # TEST
        self._max_health = 3
        self._health = self._max_health
        health_bar_offset_x = sum(divmod(self.root.width, 2))
        health_bar_offset_x = self.root.width // 2 - (self._max_health + 2) // 2
        # health_bar_offset_x = 16 # DEV
        self._health_bar = HealthBar(self, capacity=self._max_health, x=health_bar_offset_x)
        self._compass = Compass(self, x=0, y=0)
        self._node_counter = NodeCounter(self, x=(self.root.width -7), y=0)

    @property
    def health(self) -> int:
        return self._health
    
    @health.setter
    def health(self, value: int) -> None:
        self._health = value
        self._health_bar.current = value

    def _update(self, delta: float) -> None:
        if not self._is_moving:
            if not keyboard.is_pressed("e"):
                self._is_moving = True
                self._marker.is_moving = False
                self.target = self._marker.position
            return
        
        if keyboard.is_pressed("1"):
            self.interact("1")
        
        elif keyboard.is_pressed("2"):
            self.interact("2")
        
        elif keyboard.is_pressed("3"):
            self.interact("3")

        if keyboard.is_pressed("f"):
            self.interact("f")

        elif keyboard.is_pressed("e"):
            self._is_moving = False
            self._marker.is_moving = True
            self._marker.visible = True
            self._marker.position = self.position

        elif keyboard.is_pressed("q"):
            self.interact("q")
        
        elif keyboard.is_pressed("space"):
            self.interact("space")

        current = self.position
        if keyboard.is_pressed("d"):
            self.x += self._SPEED * delta
        if keyboard.is_pressed("a"):
            self.x -= self._SPEED * delta
        if keyboard.is_pressed("w"):
            self.y -= self._SPEED * delta
        if keyboard.is_pressed("s"):
            self.y += self._SPEED * delta
        if self.position != current: # moved
            cx, cy = current
            self.direction[0] = self.x - cx
            self.direction[1] = self.y - cy
            if self.get_colliders(): # did collide, reset movement
                self.position = current
                return # do not send request on abortion
            # self.root.send("ATTR:x={x}:y={y}".format(x=self.x, y=self.y))
    
    def _on_collision(self, collider: Node) -> None:
        # print("COLLISION:", collider.name)
        if "Crater" in collider.name: # hit by shell
            # print("PLAYER HIT")
            self.health -= 1
