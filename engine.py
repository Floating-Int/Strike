import keyboard
from concatenate import Splicer
from clock import Clock
from node import Node
from camera import Camera

import time

# activate ANSI escape codes
import os as _os

_os.system("")
_os.system("cls") # DEV
del _os


ANSI_UP = "\u001b[A"
ANSI_DOWN = "\u001b[B"
ANSI_RIGHT = "\u001b[C"
ANSI_LEFT = "\u001b[D"


class Engine:
    def __init__(self, tps: float, width: int = 10, height: int = 5) -> None:
        self.camera = Camera.get_current()
        self.tps = tps
        self.width = int(width)
        self.height = int(height)
        self._splicer = Splicer(self.width, self.height)        
        self._clock = Clock(tps=tps)
        # start
        self.is_running = True
        self._on_start()
        self.__main_loop()
    
    @staticmethod
    def get_current_camera() -> Camera:
        return Camera.current

    def _update(self, delta: float) -> None:
        return
    
    def _update_socket(self) -> None:
        return

    def _on_start(self) -> None:
        return
    
    def __main_loop(self) -> None:
        while self.is_running: # main loop
            self._clock.tick()

            self._update_socket()

            # NOTE: update 'self' or 'Node._nodes' first?
            # delta = self._clock.get_delta()
            delta = self._clock._tick_rate
            self._update(delta)
            for node in Node._nodes:
                node._update(delta)
            
            array = self._splicer.concatenate(Node._nodes, Camera.current)
            for line in array:
                rendered = "".join(line)
                print(rendered[:self.width], "1" * 16, flush=False)
            print(ANSI_UP * len(array), end="\r")

