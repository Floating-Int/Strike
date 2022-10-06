from typing import Any
from node import Node
from animation import Animation, AnimationPlayer
import keyboard


class Player(Node):
    # states (constants)
    IDLE = 0
    ARMED = 1
    CROUCING = 2
    SHOOTING = 3
    RELOADING = 4

    def __init__(self, owner: Any = None, x: int = 0, y: int = 0, z: int = 0) -> None:
        super().__init__(owner, x, y, z)
        self.state = self.IDLE
        self.animation = AnimationPlayer(
            self,
            #mode=AnimationPlayer.FIXED,
            Idle=Animation("./animations/player/idle"),
            Equip=Animation("./animations/player/equip")
        )
        self.animation.play("Idle")
    
    def _update(self, delta: float) -> None:
        if keyboard.is_pressed("d"):
            self.x += 1
        if keyboard.is_pressed("a"):
            self.x -= 1
        
        # animation based
        if self.animation.is_playing:
            return
        
        if keyboard.is_pressed("shift"):
            if self.state != self.ARMED:
                self.state = self.ARMED
                self.animation.play("Equip")
        elif self.state != self.IDLE:
            self.state = self.IDLE
            self.animation.play("Idle")
        

        