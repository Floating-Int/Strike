from node import Node


class Interactive: # Component
    precedence: int = 10
    _interactives = []

    @staticmethod
    def __sort_fn(interactive: Node) -> None:
        return (interactive.precedence, interactive._uid)

    def __new__(cls, *args, **kwargs):
        instance = super().__new__(cls, *args, **kwargs)
        cls._interactives.append(instance)
        Interactive._interactives.sort(key=Interactive.__sort_fn)
        return instance
    
    def is_available_for(self, interactor: Node) -> bool:
        if interactor.x >= self.x and interactor.x < self.x + len(self.content[0]): # NOTE: content is rectangle shaped
            if interactor.y >= self.y and interactor.y < self.y + len(self.content):
                return True
        return False
    
    def _on_interaction(self, interactor: Node, key: str = None) -> None:
        return
    
    def free(self) -> None:
        self._interactives.remove(self)
        super().free()


class Interactor: # Component

    def interact(self, key: str = None, single: bool = True) -> None:
        for interactive in Interactive._interactives:
            if interactive == self:
                continue
            if interactive.is_available_for(self):
                interactive._on_interaction(self, key=key)
                if single:
                    break
    
    def get_available_interactive(self) -> Node:
        """Returns the first available <Interactive> based on <Interactive>.is_available_for(<Self@Interactor>)

        Returns:
            Interactive | None: available interactive
        """
        for interactive in Interactive._interactives:
            if interactive.is_available_for(self):
                return interactive
        return None

    def interact_with(self, interactive: Node, key=None) -> None:
        interactive._on_interaction(self, key=key)
