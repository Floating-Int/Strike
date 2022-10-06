from node import Node
import os


class Frame:
    def __init__(self, fpath: str) -> None:
        # NOTE: loads as square
        f = open(fpath)
        lines = f.readlines()
        longest = len(max(lines, key=len)) -1
        self.content = []
        for line in lines:
            self.content.append(list((line.rstrip("\n")).ljust(longest)))
        # self.content = list(map(lambda line: list(line.rstrip("\n")), f.readlines()))
        f.close()


class Animation:
    def __init__(self, path: str) -> None:
        fnames = os.listdir(path)
        self.frames = [Frame(os.path.join(path, fname)) for fname in fnames]

    @classmethod
    def new(cls):
        # returns an empty Animation
        instance = object.__new__(cls)
        instance.frames = []


class AnimationPlayer(Node): # TODO: add buffered animations on load
    FIXED = 0
    DELTATIME = 1
    _STD_ANIMATION = Animation.new()

    def __init__(self, owner: Node, fps: float = 16, /, mode=FIXED, **animations) -> None:
        self.owner = owner
        self.fps = fps
        self._fps_ratio = 1.0 / fps
        self.mode = mode # process mode (FIXED | DELTA)
        self.animations = dict(animations)
        self._animation = self._STD_ANIMATION
        self.is_playing = False
        self._current_frames = None
        self._next = None
        self._accumulated_time = 0
    
    def __iter__(self):
        return self

    def __next__(self) -> Frame:
        try:
            self._next = next(self._current_frames) # next of generator
            return self._next
        except StopIteration:
            self.is_playing = False
            self._current_frames = None
            self._next = None
            return None

    @property    
    def animation(self) -> Animation:
        return self._animation
    
    @animation.setter
    def animation(self, animation: str) -> None:
        self._animation = self.animations[animation]
        # make generator
        self._current_frames = (frame for frame in self._animation.frames)
        # print("CURRENT CHANGED")
        try:
            self._next = next(self._current_frames)
            # self.owner.content = self._next.content
        except StopIteration:
            self.is_playing = False
            self._current_frames = None
            self._next = None
    
    def add(self, name: str, animation: Animation) -> None:
        self.animations[name] = animation
    
    def remove(self, name: str) -> None:
        del self.animations[name]
    
    def play(self, animation: str) -> None:
        self.is_playing = True
        self._animation = animation
        self._current_frames = (frame for frame in self.animations[self.animation].frames)
        try:
            self._next: Frame = next(self._current_frames)
        except StopIteration:
            self.is_playing = False
            self._current_frames = None
            self._next: Frame = None
        if self._next != None:
            self.owner.content = self._next.content
    
    def play_backwards(self, animation: str) -> None:
        self.is_playing = True
        self._animation = animation
        # reverse order frames
        self._current_frames = (frame for frame in reversed(self.animations[self.animation].frames))
        try:
            self._next: Frame = next(self._current_frames)
        except StopIteration:
            self.is_playing = False
            self._current_frames = None
            self._next: Frame = None
        if self._next != None:
            self.owner.content = self._next.content
        
    def advance(self) -> bool:
        """Advances 1 frame

        Returns:
            bool: whether it was NOT stopped
        """
        if self._current_frames == None:
            return False
        frame = self._next
        try:
            self._next = next(self._current_frames)
        except StopIteration:
            self.is_playing = False
            self._current_frames = None
            self._next = None
        # print("FRAME:", frame)
        if frame != None:
            self.owner.content = frame.content
        return frame != None # returns true if not stopped
    
    def _update(self, delta: float) -> None:
        if self.is_playing:

            if self.mode == AnimationPlayer.FIXED:
                frame = next(self)
                if frame == None:
                    return
                self.owner.content = frame.content

            elif self.mode == AnimationPlayer.DELTATIME:
                # apply delta time
                self._accumulated_time += delta
                if self._accumulated_time >= self._fps_ratio:
                    self._accumulated_time -= self._fps_ratio # does not clear time
                    frame = next(self)
                    self.owner.content = frame.content
