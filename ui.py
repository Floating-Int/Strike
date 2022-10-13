from cgitb import text
import math
from node import Node, Control
import keyboard


class Label(Control, Node):
    def __init__(self, owner=None, x: int = 0, y: int = 0, z: int = Control.TOP_LEVEL, text: str = None) -> None:
        super().__init__(owner, x, y, z)
        self._text = text if text is str else ""
        self.content = list(map(list, text.split("\n"))) if text is str else []
    
    @property
    def text(self) -> str:
        return self._text
    
    @text.setter
    def text(self, text: str) -> None:
        self._text = text if type(text) is str else ""
        self.content = list(map(list, text.split("\n"))) if type(text) is str else []


class DecayLabel(Label):
    def __init__(self, owner=None, x: int = 0, y: int = 0, z: int = Control.TOP_LEVEL, text: str = None, decay: float = 1.0) -> None:
        super().__init__(owner, x, y, z, text)
        self.decay = decay
        self.visible = False
        self._elapsed_time = decay

    def show(self) -> None:
        self._elapsed_time = 0        

    def _update(self, delta: float) -> None:
        if self._elapsed_time >= self.decay:
            self.visible = False
            return
        self.visible = True
        self._elapsed_time += delta


class Settings(Control, Node):
    TOP_LEVEL = 101
    _METHOD_PREFIX = "_on_"
    options = ["Help", "Keybinds", "Volume", "Exit"]
    key_toggle = "esc"
    key_accept = "enter"
    key_cycle = "tab"
    key_reverse = "shift"
    active = "> "
    passive = "  "
    
    def __init__(self, owner=None, x: int = 0, y: int = 0, z: int = TOP_LEVEL, header: str = "- SETTINGS -") -> None:
        super().__init__(owner, x, y, z)
        self.visible = False
        self._index = 0
        self.header = header
        self.content = [list(self.header)] + self._get_options()
        self._is_toggle_pressed = False
        self._is_accept_pressed = False
        self._is_cycle_pressed = False
    
    def _get_options(self) -> list:
        options = []
        for idx, option in enumerate(self.options):
            visual = (self.active if idx == self._index else self.passive) + option
            options.append(list(visual.ljust(len(self.header))))
        return options

    def _update(self, _delta: float) -> None:
        if self._is_toggle_pressed:
            if not keyboard.is_pressed(self.key_toggle):
                self._is_toggle_pressed = False
        elif keyboard.is_pressed(self.key_toggle): # toggle
            self.visible = not self.visible
            if self.visible:
                self._index = 0 # reset index
                self.content = [list(self.header)] + self._get_options()
            self._is_toggle_pressed = True
            return
        if not self.visible:
            return

        if self._is_accept_pressed:
            if not keyboard.is_pressed(self.key_accept):
                self._is_accept_pressed = False
        elif keyboard.is_pressed(self.key_accept):
            self._is_accept_pressed = True
            method_name = self._METHOD_PREFIX + self.options[self._index].lower()
            method = getattr(self, method_name)
            method() # call bound method
            return

        if keyboard.is_pressed(f"{self.key_reverse}+{self.key_cycle}"):
            if not self._is_cycle_pressed:
                self._is_cycle_pressed = True
                self._index = max(self._index -1, 0)
                self.content = [list(self.header)] + self._get_options()
        elif keyboard.is_pressed(self.key_cycle):
            if not self._is_cycle_pressed:
                self._is_cycle_pressed = True
                self._index = min(self._index +1, len(self.options) -1)
                self.content = [list(self.header)] + self._get_options()
        else:
            self._is_cycle_pressed = False
    
    def _on_help(self) -> None:
        ...
    def _on_keybinds(self) -> None:
        ...
    def _on_volume(self) -> None:
        ...
    def _on_exit(self) -> None:
        ...


class Compass(Control, Node):
    _CENTERED = "X"
    # _SYMBOLS = ["|", "\\", "―", "/", "|", "\\", "―", "/"]
    # _SYMBOLS = ["↓", "↘", "→", "↗", "↑", "↖", "←", "↙"]
    # _SYMBOLS = ["⇓", "⇘", "⇒", "⇗", "⇑", "⇖", "⇐", "⇙"] # points from origin
    _SYMBOLS = ["⇑", "⇖", "⇐", "⇙", "⇓", "⇘", "⇒", "⇗"] # points at origin

    def _update(self, delta: float) -> None:
        radians = math.atan2(*self.owner.position)
        normalized = (radians / math.pi) # can 'radians' be 0?
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
    _HEALTH_ICON = "€"
    # TODO: add colors
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


class ItemLabel(DecayLabel):
    def __init__(self, owner=None, x: int = 0, y: int = 0, z: int = Control.TOP_LEVEL, text: str = None, decay: float = 1.0, width: int = 5) -> None:
        super().__init__(owner, x, y, z, text, decay)
        self.width = width
    
    def _update(self, delta: float) -> None:
        super()._update(delta)
        self.content = [list(f"[{self.text.ljust(self.width)}]")]
    