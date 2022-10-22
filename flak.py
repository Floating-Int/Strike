from node import Node
from interaction import Interactive
from animation import AnimationPlayer, Animation
from mortar import Mortar, Shell, Crater


class FlakCrater(Crater): # Crater: Collider, Node
    def __init__(self, owner=None, x: int = 0, y: int = 0, z: int = 0) -> None:
        super().__init__(owner, x, y, z)
        self._animation.remove("Explode")
        self._animation.add("Explode", Animation("animations/flak_crater"))
        self._animation.animation = "Explode" # refresh frames in memory
        # self._animation.advance() # DEV: not needed


class FlakShell(Shell): # Shell: Node
    _CRATER_TYPE = FlakCrater


class Flak(Mortar): # Mortar: Interactive, Node
    COST = 15
    _SHELL_TYPE = FlakShell
    _FORCED_MISS_RADIUS_INCREASE = 3
    _MIN_FORCED_MISS_RADIUS = 2
    _SALVO_COUNT = 3
    _SALVO_SPREAD = 4

    def __init__(self, owner=None, x: int = 0, y: int = 0, z: int = 0) -> None:
        super().__init__(owner, x, y, z)
        self._animation = AnimationPlayer(
            self,
            Idle=Animation("./animations/flak/idle")
        )
        self._animation.play("Idle")
    


# \ ║ /
#  |╳|
# /╰-╯\

# ╭ ╮ ╯ ╰ ╱ ╲ ╳
# ┌ ┍ ┎ ┏ ┐ ┑ ┒ ┓
# └ ┕ ┖ ┗ ┘ ┙ ┚ ┛
# ┇ ║
