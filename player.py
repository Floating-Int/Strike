import math
from node import Node
from interaction import Interactor
from collision import Collider
from event import InputHandler, InputEvent
from container import Hotbar
from camera import Camera
from ui import HealthBar, Compass, Label, NodeCounter


class Marker(InputHandler, Node):
    reach = 15
    _SPEED = 16

    def __init__(self, owner=None, x: int = 0, y: int = 0, z: int = 0) -> None:
        super().__init__(owner, x, y, z)
        self.add_action("move_right", key="d")
        self.add_action("move_left", key="a")
        self.add_action("move_up", key="w")
        self.add_action("move_down", key="s")
        self.content = [["O"]]
        self.is_moving = False

    def _update(self, delta: float) -> None:
        if self.is_moving:
            current = [self.x, self.y]
            if self.is_action_pressed("move_right"):
                self.x += self._SPEED * delta
            if self.is_action_pressed("move_left"):
                self.x -= self._SPEED * delta
            if self.is_action_pressed("move_up"):
                self.y -= self._SPEED * delta
            if self.is_action_pressed("move_down"):
                self.y += self._SPEED * delta
            if [self.x, self.y] != current: # moved
                x = (self.x - self.owner.x) // 2
                y = (self.y - self.owner.y)
                length = math.sqrt(x*x + y*y)
                if length <= self.reach:
                    self.root.send(f"MARKER_POS:{self.root.cid}:{self.x}:{self.y}")
                else:
                    self.position = current


class HollowMarker(Node):
    def __init__(self, owner=None, x: int = 0, y: int = 0, z: int = 0) -> None:
        super().__init__(owner, x, y, z) # z index normally set to 2
        self.content = [["O"]]


class Player(Interactor, Collider, InputHandler, Node):
    ICON_HAS_SHELL = "[=]"
    ICON_HAS_NOT_SHELL = "[ ]"
    _SPEED = 16 # TODO: fix issue when speed is decimal using floor and ceil

    def __init__(self, owner: Node = None, x: int = 0, y: int = 0, z: int = 0) -> None:
        super().__init__(owner, x, y, z)
        self.add_action("move_right", key="d")
        self.add_action("move_left", key="a")
        self.add_action("move_up", key="w")
        self.add_action("move_down", key="s")
        self.add_action("activate", key="space")
        self.add_action("interact", key="f")
        self.add_action("move_marker", key="e")
        self.add_action("progress", key="c")
        self.add_action("slot_1", key="1")
        self.add_action("slot_2", key="2")
        self.add_action("slot_3", key="3")
        self.content = [["@"]]
        self.target = None # 2D point
        self.direction = [0, 0]
        self.has_shell = False
        self.hotbar = Hotbar(self, x=self.root.width -4, y=self.root.height - 10, decay=3.0)
        self.marker = Marker(self, z=2)
        self.marker.visible = False # TEST
        self.shell_indicator = Label(self, x=12, y=self.root.height -1, text=self.ICON_HAS_NOT_SHELL)
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

    def _input(self, event: InputEvent) -> None:
        if event.pressed:
            if event.action == "progress":
                self.interact("progress")

    def _update(self, delta: float) -> None:
        if self.root.settings.visible:
            return
        if not self._is_moving:
            if self.is_action_released("move_marker"):
                self._is_moving = True
                self.marker.is_moving = False
                self.target = self.marker.position
                self.interact("stop_marker")
            return
        
        if self.is_action_pressed("interact"): # interaction key
            self.interact("interact", single=False)

        elif self.is_action_pressed("move_marker"):
            self._is_moving = False
            self.marker.is_moving = True
            self.marker.visible = True
            self.marker.position = self.position

        elif self.is_action_pressed("activate"): # activation key
            self.interact("activate")
        
        # elif self.is_action_pressed("progress"):
        #     self.interact("progress")
        
        current = self.position
        if self.is_action_pressed("move_right"):
            self.x += self._SPEED * delta
        if self.is_action_pressed("move_left"):
            self.x -= self._SPEED * delta

        if self.x != current[0]: # moved on x axix
            cx = current[0]
            self.direction[0] = self.x - cx
            if self.get_colliders(): # did collide, reset x movement
                self.x = current[0]
        else:
            self.direction[0] = 0

        if self.is_action_pressed("move_up"):
            self.y -= self._SPEED * delta
        if self.is_action_pressed("move_down"):
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
