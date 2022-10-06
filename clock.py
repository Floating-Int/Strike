import time


class Clock:
    """Clock to make sure the mainloop don't run too fast
    """

    def __init__(self, tps: float) -> None:
        """Clock object to limit tick speed
        Args:
            tps (float): ticks per second
        """
        self.tps = tps
        self._tick_rate = 1.0 / tps
        self._last = time.time()

    def tick(self) -> None:
        """Waits until time since last tick is
        greater than or equal to 1 second / ticks per second
        """
        now = time.time()
        diff = now - self._last
        recover = self._tick_rate - diff
        self._last = now
        if recover > 0:
            time.sleep(recover)
        self._last = time.time()
    
    def get_delta(self) -> float: # FIXME
        now = time.time()
        delta = now - self._last
        if delta > 0:
            return delta
        return 0
