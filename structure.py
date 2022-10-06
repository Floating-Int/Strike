# Add research like features later? Unlockable buildings?

class Structure:
    COST = 1 # in resources
    HP = 1 # hit points

    def __new__(cls: type, *args, **kwargs):
        instance = super().__new__(cls)
        # adds 'hp' to every <Structure>
        instance.hp = __class__.HP
        return instance
