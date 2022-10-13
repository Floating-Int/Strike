

class Interactive:
    _interactives = []

    def __new__(cls, *args, **kwargs):
        instance = super().__new__(cls, *args, **kwargs)
        cls._interactives.append(instance)
        instance.precedence = 10
        return instance
    
    @staticmethod
    def __sort_fn(interactive) -> None:
        return (interactive.precedence, interactive._uid)
    
    @classmethod
    def _sorted_interactives(cls) -> list:
        return sorted(cls._interactives, key=cls.__sort_fn, reverse=True)
    
    def is_available_for(self, interactor) -> bool:
        if interactor.x >= self.x and interactor.x < self.x + len(self.content[0]):
            if interactor.y >= self.y and interactor.y < self.y + len(self.content):
                return True
        return False
    
    def _on_interaction(self, interactor, key: str = None) -> None:
        return
    
    def free(self) -> None:
        self._interactives.remove(self)
        super().free()


class Interactor:

    def interact(self, key: str = None, single: bool = True) -> None:
        for interactive in Interactive._sorted_interactives():
            if interactive == self:
                continue
            if interactive.is_available_for(self):
                interactive._on_interaction(self, key=key)
                if single:
                    break
    
    def interact_with(self, interactive, key=None) -> None:
        interactive._on_interaction(self, key=key)
