from node import Node
from interaction import Interactor
from collision import Collider
from container import Hotbar
from camera import Camera
from ui import HealthBar, Compass, NodeCounter
import keyboard


class Marker(Node):
    _SPEED = 16

    def __init__(self, owner=None, x: int = 0, y: int = 0, z: int = 0) -> None:
        super().__init__(owner, x, y, z)
        self.content = [["O"]]
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
                self.root.send(f"MARKER_POS:{self.root.cid}:{self.x}:{self.y}")


class HollowMarker(Node):
    def __init__(self, owner=None, x: int = 0, y: int = 0, z: int = 0) -> None:
        super().__init__(owner, x, y, z) # z index normally set to 2
        self.content = [["O"]]


class Player(Interactor, Collider, Node):
    _SPEED = 16 # TODO: fix issue when speed is decimal using floor and ceil

    def __init__(self, owner: Node = None, x: int = 0, y: int = 0, z: int = 0) -> None:
        super().__init__(owner, x, y, z)
        self.content = [["@"]]
        self.target = None # 2D point
        self.direction = [0, 0]
        self.hotbar = Hotbar(self, x=0, y=2)
        self.marker = Marker(self, z=2)
        self.marker.visible = False # TEST
        self._key_r_pressed = False
        self._is_moving = True
        self._max_health = 3
        self._health = self._max_health
        health_bar_offset_x = sum(divmod(self.root.width, 2))
        health_bar_offset_x = self.root.width // 2 - (self._max_health + 2) // 2
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
        if self._health <= 0:
            self._on_death()
        
    def _on_death(self) -> None:
        # TODO: activate spectator mode | or have 2 lives (3hp each)?
        self.position = [0, 0] # DEV
        self.health = self._max_health
        self.root.send(f"PLAYER_POS:{self.root.cid}:{self.x}:{self.y}")

    def _update(self, delta: float) -> None:
        if self.root.settings.visible:
            return
        if not self._is_moving:
            if not keyboard.is_pressed("e"):
                self._is_moving = True
                self.marker.is_moving = False
                self.target = self.marker.position
                self.interact("e_released")
            return
        
        if keyboard.is_pressed("1"):
            self.interact("1")
        
        elif keyboard.is_pressed("2"):
            self.interact("2")
        
        elif keyboard.is_pressed("3"): # DEV
            self.interact("3")
        
        if keyboard.is_pressed("tab"):
            self.interact("tab")

        if keyboard.is_pressed("f"): # interaction key
            self.interact("f", single=False)

        elif keyboard.is_pressed("e"):
            self._is_moving = False
            self.marker.is_moving = True
            self.marker.visible = True
            self.marker.position = self.position

        elif keyboard.is_pressed("q"):
            self.interact("q")
        
        elif keyboard.is_pressed("space"): # activation key
            self.interact("space")
        
        elif keyboard.is_pressed("r"):
            if not self._key_r_pressed:
                self._key_r_pressed = True
                self.interact("r")
        elif not keyboard.is_pressed("r"):
            self._key_r_pressed = False

        current = self.position
        if keyboard.is_pressed("d"):
            self.x += self._SPEED * delta
        if keyboard.is_pressed("a"):
            self.x -= self._SPEED * delta

        if self.x != current[0]: # moved on x axix
            cx = current[0]
            self.direction[0] = self.x - cx
            if self.get_colliders(): # did collide, reset x movement
                self.x = current[0]
        else:
            self.direction[0] = 0

        if keyboard.is_pressed("w"):
            self.y -= self._SPEED * delta
        if keyboard.is_pressed("s"):
            self.y += self._SPEED * delta
        
        if self.y != current[1]: # moved on y axix
            cy = current[1]
            self.direction[1] = self.y - cy
            if self.get_colliders(): # did collide, reset y movement
                self.y = current[1]
        else:
            self.direction[1] = 0
        if current != self.position:
            self.root.send(f"PLAYER_POS:{self.root.cid}:{self.x}:{self.y}")

    def _on_collision(self, collider: Node) -> None:
        # print("COLLISION:", collider.name)
        if "Crater" in collider.name: # hit by shell
            # print("PLAYER HIT")
            self.health -= 1


class HollowPlayer(Collider, Node):
    def __init__(self, owner=None, x: int = 0, y: int = 0, z: int = 0) -> None:
        super().__init__(owner, x, y, z) # z index normally set to 1
        self.content = [["@"]]
        self.shape.width = 1
        self.shape.height = 1
