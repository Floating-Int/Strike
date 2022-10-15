from node import Node, Control
from singleton import Singleton
import math


class ResourceSystem(Singleton, Control, Node): # singleton
    efficiency = 1.00 + 2.45 * 2 # DEV # percent %
    resources: float = 0.0 + 45 * 2 # DEV
    capacity: int = 80
    _elapsed_time = 0
    _SESSION = 10 / 10 # DEV # per (n)th second
    
    def _update(self, delta: float) -> None:
        self._elapsed_time += delta
        if self._elapsed_time >= self._SESSION:
            self._elapsed_time -= self._SESSION
            self.resources = min(self.resources + self.efficiency, self.capacity)
        
        width = len(str(self.capacity))
        self.content = [list(
            f"[{round(self.efficiency * 100)}% {str(math.floor(self.resources)).rjust(width)}/{self.capacity}]"
        )]
