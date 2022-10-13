import math
import random
from node import Node
from interaction import Interactive
from collision import Collider, Area
from container import Container
from animation import AnimationPlayer, Animation
from structure import Structure
# from pygame import mixer
# mixer.init()


class Crater(Collider, Node):
    _FREQUENCY = 0.1

    def __init__(self, owner=None, x: int = 0, y: int = 0, z: int = 0) -> None:
        super().__init__(owner, x, y, z)
        self.content = [["#"]]
        self._animation = AnimationPlayer(
            self,
            Explode=Animation("./animations/crater")
        )
        self._animation.animation = "Explode"
        self._animation.advance() # DEV: not needed
        # self.x -= sum(divmod(len(max(self.content, key=len)), 2))
        self.x -= len(max(self.content, key=len)) // 2 -1
        self.y -= len(self.content) // 2
        self._stage = 0
        self._start_x = x
        self._start_y = y
        self._elapsed_time = 0
        self._detected = []
    
    def _update(self, delta: float) -> None:
        if self._stage == -1:
            return
        self._elapsed_time += delta
        if self._elapsed_time > self._FREQUENCY:
            self._elapsed_time = 0
            if not self._animation.advance():
                self.shape.disabled = True
                self._stage = -1
                self._detected = [] # clear refs
                self._animation.free() # save on memory by deleting nodes not in use
                return
            self._stage += 1
            if self._stage == len(self._animation.animation.frames) -2: # next last frame
                for idx, line in enumerate(self.content):
                    if random.randint(0, 1):
                        self.content[idx] = list(reversed(line))
            self._do_collision_check()
        
    def _do_collision_check(self) -> None:
        for collider in self.get_colliders():
            if collider in self._detected:
                continue
            self.collide_with(collider)
            self._detected.append(collider)
    
    def is_colliding_with(self, collider: Node) -> bool:
        x = collider.x - self._start_x
        y = collider.y - self._start_y
        length = math.sqrt(x*x + y*y)
        # FIXME: fix calculation and origin
        if length < float(len(self.content[0])) / 2: # content is rectangle shaped
            return True
        return self.shape.is_intersecting(collider.shape)


class Shell(Node):
    _CRATER_TYPE = Crater
    _FALLING_SPEED_FACTOR = 2.5
    _MIN_LENGTH = 5
    # _sound = mixer.Sound("./sounds/mortar_impact.wav")
    
    def __init__(self, owner=None, x: int = 0, y: int = 0, z: int = 0, velocity: int = 10, target: tuple = (0, 0)) -> None:
        super().__init__(owner, x, y, z)
        self.content = [["^"]]
        self._velocity = velocity
        self._start = (x, y)
        self._target = target
        tx, ty = target
        rx = tx - x
        ry = ty - y
        self._total_length = max(self._MIN_LENGTH, math.sqrt(rx * rx + ry * ry)) # total
        self._elapsed_time = 0
        self._has_notified = False # notified server
        # self._playing_sound = False
    
    @classmethod
    def from_request(cls, args: list, kwargs: dict):
        x = kwargs["x"]
        y = kwargs["y"]
        tx = kwargs["tx"]
        ty = kwargs["ty"]
        instance = cls(x=x, y=y)
        instance._target = (tx, ty) # important because of snap to target
        return instance
    
    def _explode(self) -> None:
        self._elapsed_time = 0
        # make unreferenced Node
        self._CRATER_TYPE(None, *self._target)
        self.visible = False
        self.free()

    def _update(self, delta: float) -> None:
        self._elapsed_time += delta
        if (self._elapsed_time * self._velocity * 0.50) < (self._total_length):
            self.y -= self._velocity * delta
        elif (self._elapsed_time * self._velocity * 0.25) < (self._total_length):
            # if not self._playing_sound:
            #     self._playing_sound = True
            #     self._sound.play()
            # networking
            # move shell
            self.content = [["v"]]
            self.x = self._target[0]
            if not self._has_notified: # so clients can hear sound
                # tx, ty = self._target
                # self.root.send(self._REQUEST_FALLING.format(x=self.x, y=self.y, tx=tx, ty=ty))
                self._has_notified = True
            self.y += self._velocity * delta * self._FALLING_SPEED_FACTOR # increased impact speed
            if self._target[1] - self.y < 0.5: # snap
                self.position = self._target
                self._explode()


class Mortar(Area, Interactive, Container, Structure, Node):
    COST = 10
    _SHELL_TYPE = Shell
    _SHELL_OFFSET = [2, 1]
    _SALVO_COUNT = 1
    _SALVO_SPREAD = 0
    _FORCED_MISS_RADIUS_INCREASE = 3
    _MIN_FORCED_MISS_RADIUS = 2
    _REQUEST_SHELL_LAUNCHED = "SHELL_LAUNCHED:{type}:{x}:{y}:{tx}:{ty}"

    def __init__(self, owner=None, x: int = 0, y: int = 0, z: int = 0) -> None:
        super().__init__(owner, x, y, z)
        self.animation = AnimationPlayer(
            self,
            Idle=Animation("./animations/mortar/idle")
        )
        self.animation.play("Idle")
        self.shape.width = len(max(self.content, key=len))
        self.shape.height = len(self.content)
        self.shape.disabled = False
        self._target = None
        self._forced_miss_radius = self._MIN_FORCED_MISS_RADIUS # lower number is more accurate
        self._loaded = False
        self._shell = None
        # self._sound = mixer.Sound("./sounds/mortar_activate.wav")
    
    def set_target(self, target: list) -> None:
        self._target = target
        self._forced_miss_radius = self._MIN_FORCED_MISS_RADIUS
    
    def _on_interaction(self, interactor: Node, key: str = None) -> None:
        if key == "f":
            if interactor.target == None: # DEV may want to change this
                return
            self.set_target(interactor.target)
            # interactor.target = None # DEV may want to change this
            return
        elif key != "space":
            return # key for activation is "space"
        if self._target == None:
            return
        # instantiate projectile shell
        self._spawn_projectiles()
        self._forced_miss_radius += self._FORCED_MISS_RADIUS_INCREASE
        # self._sound.play()
    
    def _spawn_projectiles(self) -> None: # spawn projectile(s)
        type_name = self._SHELL_TYPE.__name__
        # apply forced miss radius
        tx = self._target[0] + random.randint(-self._forced_miss_radius, self._forced_miss_radius)
        ty = self._target[1] + random.randint(-self._forced_miss_radius, self._forced_miss_radius)
        # apply offset
        x = self.x + self._SHELL_OFFSET[0]
        y = self.y + self._SHELL_OFFSET[1]
        for _ in range(self._SALVO_COUNT):
            local_tx = tx + random.randint(-self._SALVO_SPREAD, self._SALVO_SPREAD)
            local_ty = ty + random.randint(-self._SALVO_SPREAD, self._SALVO_SPREAD)
            # create unreferenced nodes
            self._SHELL_TYPE(None, x=x, y=y, z=1, target=[local_tx, local_ty])
            # send request per projectile
            self.root.send(self._REQUEST_SHELL_LAUNCHED.format(type=type_name, x=x, y=y, tx=tx, ty=ty))
    
    def _on_collision(self, collider: Collider):
        self.hp -= 1
        if self.hp <= 0:
            print("HIT")
