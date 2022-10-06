from node import Node, Control
import math


class Singleton:
    _instances = {}

    def __new__(cls: type, *args, **kwargs):
        if not cls in Singleton._instances:
            instance = super().__new__(cls)
            Singleton._instances[cls] = instance
            return instance
        return Singleton._instances[cls]


class ResourceSystem(Singleton, Control, Node): # singleton
    efficiency = 1.00 + 2.45 # percent %
    resources: float = 0.0 + 45
    capacity: int = 80
    _elapsed_time = 0
    _SESSION = 10 / 10# per (n)th second
    
    def _update(self, delta: float) -> None:
        self._elapsed_time += delta
        if self._elapsed_time >= self._SESSION:
            self._elapsed_time -= self._SESSION
            self.resources = min(self.resources + self.efficiency, self.capacity)
        
        width = len(str(self.capacity))
        self.content = [list(
            f"[{round(self.efficiency * 100)}% {str(math.floor(self.resources)).rjust(width)}/{self.capacity}]"
        )]
