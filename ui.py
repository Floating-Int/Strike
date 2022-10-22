import math
from functools import wraps
from types import FunctionType
from node import Node, Control
from event import InputHandler, InputEvent


class Label(Control, Node):
    def __init__(self, owner=None, x: int = 0, y: int = 0, z: int = Control.TOP_LEVEL, text: str = None) -> None:
        super().__init__(owner, x, y, z)
        self._text = text if type(text) is str else ""
        self.content = list(map(list, text.split("\n"))) if type(text) is str else []
    
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


# class Option:
#     __slots__ = ("text", "callback")

#     def __init__(self, text: str, callback: Callable) -> None:
#         self.text = text
#         self.callback = callback


class Settings(InputHandler, Control, Node):
    TOP_LEVEL = 101
    _METHOD_PREFIX = "_on_"
    _FILLER = " "
    
    def __init__(self, owner=None, x: int = 0, y: int = 0, z: int = TOP_LEVEL, header: str = "- SETTINGS -", active: str = "> ", passive: str = "  ") -> None:
        super().__init__(owner, x, y, z)
        self.header = header
        self.active = active # TODO: change to private
        self.passive = passive
        self.add_action("toggle", "esc")
        self.add_action("accept", "enter")
        self.add_action("cycle", "tab")
        self.add_action("reverse", "shift") # used in combination with 'cycle' action
        self.visible = False
        self.content = [list(self.header)]
        self._options = {} # name: function
        self._index = 0
        # self._longest_len = len(max(list(self._options.keys()) + [self.header], key=len)) if self._options else 0
        self._longest_len = len(self.header)

    # decorator    
    def option(self, option: FunctionType) -> Warning:
        """Decorator for adding options

        Args:
            option (FunctionType): function representing an option

        Returns:
            Callable: do not call this
        """
        # if option.__code__.co_varnames == tuple():
        #     raise TypeError(f"{option.__name__} requres an argument, which will be used to display the option")
        name = option.__name__.partition(self._METHOD_PREFIX)[2].capitalize()
        self._options[name] = option
        # self._longest_len = len(max(list(self._options.keys()) + [self.header], key=len)) if self._options else 0
        self._longest_len = len(self.header)
        self._refresh_content()

        @wraps(option)
        def uncallable() -> Exception:
            raise NotImplementedError("only use <Settings>.option as a decorator for registering an option")
        return uncallable

    def _refresh_content(self):
        # line = f"{self.[state]}{option.__code__.co_varnames[-1]}"
        self.content = [list(self.header)]
        for idx, name in enumerate(self._options.keys()):
            if idx == self._index:
                # line = self.active + name.ljust(self._longest_len, self._FILLER)
                line = (self.active + name).ljust(self._longest_len, self._FILLER)
            else:
                # line = self.passive + name.ljust(self._longest_len, self._FILLER)
                line = (self.passive + name).ljust(self._longest_len, self._FILLER)
            self.content.append(list(line))

    def _input(self, event: InputEvent) -> None:
        if event.pressed:
            if event.action == "toggle":
                self.visible = not self.visible
                if not self.visible:
                    self._index = 0
                    self._refresh_content()

            elif not self.visible:
                return

            elif event.action == "cycle":
                if self.is_action_pressed("reverse"):
                    self._index = max(self._index -1, 0)
                else:
                    self._index = min(self._index +1, len(self._options) -1)
                self.content = [list(self.header)]
                self._refresh_content()
            
            elif event.action == "accept":
                method = list(self._options.values())[self._index]
                method()


class Compass(Control, Node):
    _CENTERED = "X"
    # _SYMBOLS = ["|", "\\", "―", "/", "|", "\\", "―", "/"]
    # _SYMBOLS = ["↓", "↘", "→", "↗", "↑", "↖", "←", "↙"]
    # _SYMBOLS = ["⇓", "⇘", "⇒", "⇗", "⇑", "⇖", "⇐", "⇙"] # points from origin
    _SYMBOLS = ["⇑", "⇖", "⇐", "⇙", "⇓", "⇘", "⇒", "⇗"] # points at origin

    def _update(self, _delta: float) -> None:
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
    
    def _update(self, _delta: float) -> None:
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
    