from animation import AnimationPlayer, Animation, Frame
from camera import Camera
from engine import Engine
from nodes import *
from wall import Wall
from collision import Collider, Shape, ReactiveShape
import keyboard

TPS = 16
WIDTH = 20
HEIGHT = 10


class Player(Collider, Node):
    SPEED = 1

    def __init__(self, owner=None, x: int = 0, y: int = 0, z: int = 0) -> None:
        super().__init__(owner, x, y, z)
        self.content = [["@"]]
        self._node_counter = NodeCounter(self, x=self.root.width-7)
        
    def _update(self, _delta: float) -> None:
        current = self.position
        if keyboard.is_pressed("d"):
            self.x += self.SPEED
        if keyboard.is_pressed("a"):
            self.x -= self.SPEED
        if keyboard.is_pressed("w"):
            self.y -= self.SPEED
        if keyboard.is_pressed("s"):
            self.y += self.SPEED
        if self.get_colliders():
            self.position = current
        Camera.current.x = self.x - self.root.width  // 2
        Camera.current.y = self.y - self.root.height // 2 


class DebugEngine(Engine):
    
    def _on_start(self) -> None:
        Node.root = self
        self.player = Player(z=1)
        self.animation = AnimationPlayer(
            self.player,
            DebugAnimation=Animation("animations/debug")
        )
        # self.wall_small = Wall(x=5)
        self.wall_large = Wall(x=5, y=2, width=5, height=3)
        self.walls = []

    def _update(self, _delta: float) -> None:
        if keyboard.is_pressed("q"): # create
            self.walls.append(Wall(x=self.player.x, y=self.player.y +1))
        if keyboard.is_pressed("f"): # destroy
            for wall in self.walls:
                wall.free()
            self.walls = []


if __name__ == "__main__":
    engine = DebugEngine(TPS, WIDTH, HEIGHT)
