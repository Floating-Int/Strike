import math
from node import Node, Control
import keyboard


class Settings(Control, Node):
    def __init__(self, owner=None, x: int = 0, y: int = 0, z: int = Control.TOP_LEVEL) -> None:
        super().__init__(owner, x, y, z)
        self.visible = False
        self.content = [list(
            "- SETTINGS -"
        )]
    
    def _update(self, _delta: float) -> None:
        if keyboard.is_pressed("esc"):
            self.visible = not self.visible


class Compass(Control, Node):
    _CENTERED = "X"
    _SYMBOLS = ["|", "\\", "―", "/", "|", "\\", "―", "/"]
    _SYMBOLS = ["↓", "↘", "→", "↗", "↑", "↖", "←", "↙"]
    _SYMBOLS = ["⇓", "⇘", "⇒", "⇗", "⇑", "⇖", "⇐", "⇙"] # points from origin
    _SYMBOLS = ["⇑", "⇖", "⇐", "⇙", "⇓", "⇘", "⇒", "⇗"] # points at origin

    def _update(self, delta: float) -> None:
        # self.x = self.owner.x - 18 # TODO: make this automatic
        # self.y = self.owner.y - 6
        radians = math.atan2(*self.owner.position)
        # idx = int(round((radians * 100) // 8))
        # symbol = self._SYMBOLS[idx]
        normalized = (radians / math.pi)
        if normalized == 0:
            symbol = self._SYMBOLS[0]
        else:
            idx = int(round(normalized * 4))
            symbol = self._SYMBOLS[idx]
        if self.owner.position == [0, 0]:
            symbol = self._CENTERED
        y = self.owner.y * -1 # swapped for visual
        self.content = [list(
            f"[{str(int(self.owner.x)).rjust(3)}, {str(int(y)).rjust(3)}]({symbol})"
        )]


class HealthBar(Control, Node):
    MAXIMUM = None
    _HEALTH_ICON = "|"
    _HEALTH_ICON = "€"
    # _COLOR = "\u001b[32;1m"
    # _RESET = "\u001b[0m"
    _COLOR = ""
    _RESET = ""

    def __init__(self, owner=None, x: int = 0, y: int = 0, z: int = Control.TOP_LEVEL, capacity: int = 1, current: int = MAXIMUM) -> None:
        super().__init__(owner, x, y, z)
        self.capacity = capacity
        self.current = capacity if current == self.MAXIMUM else current
    
    def _update(self, delta: float) -> None:
        # self.x = self.owner.x - sum(divmod(self.capacity, 2))
        # self.y = self.owner.y - sum(divmod(self.root.height, 2))
        health = (self._HEALTH_ICON * self.current).ljust(self.capacity)
        self.content = [list(
            f"[{health.ljust(self.capacity)}]"
        )]
        self.content = [["[" + self._COLOR]
                        + list(health)
                        + [self._RESET + "]"]]


class NodeCounter(Control, Node):
    def _update(self, _delta: float) -> None:
        self.content = [[f"[{str(len(self._nodes)).rjust(5)}]"]]


class Label(Control, Node):
    def __init__(self, owner=None, x: int = 0, y: int = 0, z: int = Control.TOP_LEVEL, text: str = None) -> None:
        super().__init__(owner, x, y, z)
        self.text = text if text != None else ""
    
    def _update(self, _delta: float) -> None:
        self.content = [list(
            f"[{self.text.ljust(self._longest_len)}]"
        )]


class ItemLabel(Label):
    def __init__(self, owner=None, x: int = 0, y: int = 0, z: int = Control.TOP_LEVEL, text: str = None, width: int = 5, decay: float = 2.0) -> None:
        super().__init__(owner, x, y, z, text)
        self.width = width
        self.decay = decay
        self.visible = False
        self._elapsed_time = decay
    
    def _update(self, delta: float) -> None:
        if self._elapsed_time >= self.decay:
            self.visible = False
            return
        self._elapsed_time += delta
        self.content = [list(
            f"[{self.text.ljust(self.width)}]"
        )]
    
    def show(self) -> None: # show briefly
        self.visible = True
        self._elapsed_time = 0
