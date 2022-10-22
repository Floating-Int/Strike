from node import Node
import math


class StaticControl: # Component
    """Used in combination with Node to create a static UI class

    Construct classed with relative x and y
    """
    TOP_LEVEL = 99

    def __init__(self, owner: type, x: int = 0, y: int = 0, z: int = TOP_LEVEL) -> None:
        super().__init__(owner, x, y, z)
        self.x += owner.x
        self.y += owner.y


class StaticDecayLabel(StaticControl, Node):
    def __init__(self, owner: type, x: int = 0, y: int = 0, z: int = StaticControl.TOP_LEVEL, text: str = None, decay: float = 1.0) -> None:
        super().__init__(owner, x, y, z)
        self._text = text if type(text) is str else ""
        self.content = list(map(list, text.split("\n"))) if type(text) is str else []
        self.decay = decay
        self.visible = False
        self._elapsed_time = decay
    
    @property
    def text(self) -> str:
        return self._text
    
    @text.setter
    def text(self, text: str) -> None:
        self._text = text if type(text) is str else ""
        self.content = list(map(list, text.split("\n"))) if type(text) is str else []
    
    def show(self) -> None:
        self._elapsed_time = 0
    
    def _update(self, delta: float) -> None:
        if self._elapsed_time >= self.decay:
            self.visible = False
            return
        self.visible = True
        self._elapsed_time += delta


class ProgressBar(StaticControl, Node):
    active: str = "+"
    passive: str = "-"

    def __init__(self, owner: type, x: int = 0, y: int = 0, z: int = StaticControl.TOP_LEVEL, value: float = 0, start: float = 0, stop: float = 100, step: float = 1, length: int = 5) -> None:
        super().__init__(owner, x, y, z)
        self.content = [list()]
        self.start = start
        self.stop = stop
        self.step = step
        self.value = max(self.start, min(value, self.stop))
        self.length = length
    
    def advance(self) -> None:
        self.value = min((self.value + self.step), self.stop)
        diff = (self.stop - self.start)
        segment = self.length / diff
        filled = math.ceil(segment * (self.value - self.start))
        remaining = self.length - filled # FIXME: may break when member 'stop' is float
        self.content = [list(f"([{(self.active * filled).ljust(remaining, self.passive)}])")]
    
    def reset(self) -> None:
        self.value = self.start
        self.content = [list(f"|[{self.passive * self.length}]")]
