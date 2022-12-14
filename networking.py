from typing import Any
from node import Node


# class Hollow: # TODO: move class to a different file
#     def __new__(cls: type, *args, **kwargs) -> type:
#         instance = Node.__new__(cls)
#         return instance # NOTE: still needs to manually send requests


class Informative: # PROTOTYPE
    """ NOTE: Classes deriving from 'Informative' has to specify 'Informative' last """
    _REQUEST_ATTR_UPDATE = "ATTR:{name}:{value}"

    def __new__(cls, *args, **kwargs):
        instance = object.__new__(cls)
        instance.notify = []
        return instance
    
    def __setattr__(self, name: str, value: Any) -> None:
        object.__setattr__(self, name, value)
        if name in self.notify:
            self.root.send(self._REQUEST_ATTR_UPDATE.format(name=name, value=value))