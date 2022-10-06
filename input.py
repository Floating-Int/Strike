import threading
import keyboard


class _Input:
    _registry = []
    # init class
    
    @classmethod
    def is_pressed(cls, key: str) -> bool:
        return key in cls._registry
