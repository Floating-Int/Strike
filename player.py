from node import Node
from interaction import Interactor
from collision import Collider
from event import InputHandler, InputEvent
from container import Hotbar
from camera import Camera
from ui import HealthBar, Compass, NodeCounter


class Marker(InputHandler, Node):
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
            current = (self.x, self.y)
            if self.is_action_pressed("move_right"):
                self.x += self._SPEED * delta
            if self.is_action_pressed("move_left"):
                self.x -= self._SPEED * delta
            if self.is_action_pressed("move_up"):
                self.y -= self._SPEED * delta
            if self.is_action_pressed("move_down"):
                self.y += self._SPEED * delta
            if (self.x, self.y) != current: # moved
                self.root.send(f"MARKER_POS:{self.root.cid}:{self.x}:{self.y}")


class HollowMarker(Node):
    def __init__(self, owner=None, x: int = 0, y: int = 0, z: int = 0) -> None:
        super().__init__(owner, x, y, z) # z index normally set to 2
        self.content = [["O"]]


class Player(Interactor, Collider, InputHandler, Node):
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
        self.add_action("build", key="q")
        self.add_action("rotate", key="r")
        self.add_action("slot_1", key="1")
        self.add_action("slot_2", key="2")
        self.add_action("slot_3", key="3")
        self.add_action("cycle_next", key="tab")
        self.content = [["@"]]
        self.target = None # 2D point
        self.direction = [0, 0]
        self.hotbar = Hotbar(self, x=0, y=2)
        self.marker = Marker(self, z=2)
        self.marker.visible = False # TEST
        # self._key_r_pressed = False
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
        if event.action == "rotate" and event.pressed:
            self.interact("r")

    def _update(self, delta: float) -> None:
        if self.root.settings.visible:
            return
        if not self._is_moving:
            if self.is_action_released("move_marker"):
                self._is_moving = True
                self.marker.is_moving = False
                self.target = self.marker.position
                self.interact("e_released")
            return
        
        if self.is_action_pressed("slot_1"):
            self.interact("1")
        
        elif self.is_action_pressed("slot_2"):
            self.interact("2")
        
        elif self.is_action_pressed("slot_3"):
            self.interact("3")
        
        if self.is_action_pressed("cycle_next"):
            self.interact("tab")

        if self.is_action_pressed("interact"): # interaction key
            self.interact("f", single=False)

        elif self.is_action_pressed("move_marker"):
            self._is_moving = False
            self.marker.is_moving = True
            self.marker.visible = True
            self.marker.position = self.position

        elif self.is_action_pressed("build"):
            self.interact("q")
        
        elif self.is_action_pressed("activate"): # activation key
            self.interact("space")
        
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
