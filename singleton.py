

class Singleton: # NOTE: should be the latest parent class
    # TODO: add system for making every method a classmethod (that still uses self)
    _PREFIX = "_singleton"

    def __new__(cls: type, *args, **kwargs):
        if not hasattr(cls, Singleton._PREFIX):
            instance = super().__new__(cls)
            setattr(cls, Singleton._PREFIX, instance)
            return instance
        return getattr(cls, Singleton._PREFIX)