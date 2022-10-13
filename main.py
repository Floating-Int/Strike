from client import Client
from engine import Engine
from report import BugReport
from systems import *
from nodes import *
from items import *
from dev import *


TPS = 16 / 1
WIDTH = 24 * 1.5 * 2
WIDTH = 73
HEIGHT = 6 * 2
HEIGHT = 13
HOST = "localhost"
PORT = 7070


class App(Client, Engine):
    REQUEST_DISCONNECT = "DISCONNECT:{cid}"
    REQUEST_PLAYER_JOINED = "PLAYER_JOINED:{x}:{y}"

    def __init__(self, tps: int = 16, width: int = 10, height: int = 5, host: str = "localhost", port: int = 8080) -> None:
        self.cid = None
        self.clients = {} # TODO: on connection, receive total connected clients 
        self.markers = {}
        Client.__init__(self, host, port)
        Engine.__init__(self, tps, width, height)

    def _on_start(self) -> None:
        Node.root = self # important
        self.camera = Camera.get_current() # main camera
        self.settings = Settings(x=2, y=2)
        self.settings._on_exit = self.disconnect
        self.player = Player(self, x=3, y=3, z=1)
        self.player.hotbar.add_item(Wrench(self.player))
        self.player.hotbar.add_item(RemoteTrigger(self.player))
        # self.player.hotbar.add_item(Firearm(self.player))
        self.settings.owner = self.player
        self.resource_system = ResourceSystem(self.player, x=0, y=self.height-1)
        # self.player.wrench = Wrench(self.player)
        # self.player.remote_trigger = RemoteTrigger(self.player)
        # self.player.firearm = Firearm(self.player)
        self.moartar_a = Mortar(self, x=10, y=2)
        self.moartar_b = Mortar(self, x=10, y=6)
        self.flak_a = Flak(self, x=-10, y=2)
        self.depot = Depot(self, x=4, y=2)
        # request join
        self.send(self.REQUEST_PLAYER_JOINED.format(x=self.player.x, y=self.player.y))
    
    def _update(self, delta: float) -> None:
        self.camera.x, self.camera.y = self.player.x-WIDTH//2, self.player.y-HEIGHT//2

    @staticmethod
    def decode_payload(payload: tuple) -> tuple: # (args, kwargs)
        args = []
        kwargs = {}
        for i, arg in reversed(tuple(enumerate(payload))):
            if "=" in arg:
                k, v = arg.split("=")
                if v == "None":
                    v = None
                else:
                    try:
                        v2 = v
                        v = float(v)
                    except ValueError:
                        v = v2
                kwargs[k] = v
                # args.pop(i)
            elif arg == "None":
                arg = None
            else:
                try:
                    arg2 = float(arg)
                    args.append(arg2)
                except ValueError:
                    args.append(arg)
        args = tuple(reversed(args))
        kwargs = {k: v for k, v in reversed(kwargs.items())}
        return args, kwargs

    def on_player_spawn(self, cid: int, x: int, y: int):
        # TODO: send back player position
        # print(f"NEW PLAYER ({cid}) at {x}x, {y}y")
        if self.cid == cid:
            ...
            self.player.position = [x +19, y +2] # DEV
        else:
            hollow_player = HollowPlayer(x=x, y=y, z=1)
            self.clients[cid] = hollow_player
        # spawn base
        # x, y = 0, -5 # DEV
        w, h = 18, 7
        w2, h2 = 5, 5
        door_w = [3, 4, 5, 6, 7]
        Mortar(x=x+3, y=y+2)
        Depot(x=x+10, y=y+2)
        for a in range(w):
            Wall(x=x+a, y=y)
            if not a in door_w:
                Wall(x=x+a, y=y+h-1)
        for a in range(w, w+w2):
            Wall(x=x+a, y=y)
            Wall(x=x+a, y=y+h2-1)
        for b in range(1, h-1):
            Wall(x=x, y=y+b)
        for b in range(h2):
            Wall(x=x+w+w2, y=y+b)
        Wall(x=x+17, y=y+4)
        
    def disconnect(self) -> None:
        self.send(self.REQUEST_DISCONNECT.format(cid=self.cid))
        self._sock.close() # TODO: make disconnet interface for underlying Client
        self.is_running = False

    def _on_request(self, request: str, payload: tuple) -> None:
        args, kwargs = self.decode_payload(payload)
        if request == "CONNECTED":
            self.cid = int(args[0])
            print("CID:", self.cid)
        elif request == "DISCONNECTED": # FIXME
            cid = int(args[0])
            self.clients[cid].free() # TODO add auto support for free() on __del__()
            del self.clients[cid]
            print("DISCONNECTED CID:", cid)
        elif request == "CREATE":
            class_name = args[0]
            cls = globals()[class_name] # create unreferenced node
            instance = cls.from_request(args, kwargs)
        elif request == "PLAYER_CREATE":
            cid, x, y = tuple(map(int, args))
            self.on_player_spawn(cid, x, y)
        elif request == "PLAYER_POS":
            cid, x, y = tuple(map(int, args))
            if not cid in self.clients.keys():
                self.clients[cid] = HollowPlayer(x=x, y=y, z=1)
            self.clients[cid].position = [x, y]
        elif request == "MARKER_POS":
            cid, x, y = tuple(map(int, args))
            if not cid in self.markers.keys():
                self.markers[cid] = HollowMarker(x=x, y=y, z=2)
            self.markers[cid].position = [x, y]


if __name__ == "__main__":
    print("[Info] Started Client")
    try:
        # TODO: inside App, handle connection refused, connection not found
        app = App(TPS, WIDTH, HEIGHT, HOST, PORT)
    except Exception as exception:
        # NOTE: BugReport gathers the last exception
        report = BugReport((HOST, PORT))
        # report.submit() # DEV
        report.print_report()
        # raise type(exception) from exception
