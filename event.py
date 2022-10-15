from systems import Singleton
import keyboard


class InputEvent:
    pressed: bool = False
    action: str = ""

    def __init__(self, input_map, pressed: bool = False, action: str = "") -> None:
        self.input_map = input_map
        self.pressed = pressed
        self.action = action
    
    def is_action_pressed(self, action: str) -> bool:
        return self.input_map._states[action] # NOTE: raises error if action is not registered
    
    def is_action_released(self, action: str) -> bool:
        return not self.input_map._states[action] # NOTE: raises error if action is not registered


class InputEventAction(InputEvent):
    ...


class InputMap(Singleton):
    """Framebased InputMap
    """
    _input_handlers = []
    _keybinds = {}
    _states = {}
    _event_buffer = {}
    
    @classmethod
    def add_action(self, action: str, key: str) -> None:
        if not key in self._keybinds:
            self._keybinds[key] = []
        if not action in self._keybinds[key]:
            self._keybinds[key].append(action)
            self._states[action] = False
            keyboard.on_press_key(key, self._on_action_pressed)
            keyboard.on_release_key(key, self._on_action_released)
    
    @classmethod
    def _on_action_pressed(self, key) -> None:
        if key.name not in self._keybinds:
            return
        for action in self._keybinds[key.name]:
            event = InputEventAction(self, pressed=True, action=action)
            self._event_buffer[action] = event
    
    @classmethod
    def _on_action_released(self, key) -> None:
        if key.name not in self._keybinds:
            return
        for action in self._keybinds[key.name]:
            event = InputEventAction(self, pressed=False, action=action)
            self._event_buffer[action] = event

    @classmethod
    def _update(self):
        for key, actions in self._keybinds.items():
            if keyboard.is_pressed(key):
                for action in actions:
                    self._states[action] = True
            else:
                for action in actions:
                    self._states[action] = False
        
        for event in self._event_buffer.values():
            for input_handler in self._input_handlers:
                input_handler._input(event)
        # reset event buffer so it can collect new inputs until next frame
        self._event_buffer = {}


class InputHandler: # component

    def __new__(cls: type, *args, **kwargs) -> type:
        instance = super().__new__(cls)
        InputMap._input_handlers.append(instance)
        return instance
    
    @staticmethod
    def add_action(action: str, key: str) -> None:
        InputMap.add_action(action, key)

    @staticmethod
    def is_action_pressed(action: str) -> bool:
        return InputMap._states[action]
    
    @staticmethod
    def is_action_released(action: str) -> bool:
        return not InputMap._states[action]

    def _input(self, event: InputEvent) -> None:
        return
    
    def free(self) -> None:
        InputMap._input_handlers.remove(self)
        super().free()

