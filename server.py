from typing import Union
import socket
import selectors
import datetime
import random


class BaseServer:
    _BUFF_SIZE = 4096
    _DELIMITER = b"$"
    _ARGUMENT_DELIMITER = ":"
    _NEGATIVE_INF = float("-inf")

    def __init__(self, host: Union[str, int], port: Union[str, int], backlog: int = 5) -> None:
        self.connections = []
        self._backlog = backlog
        self._address = (host, port)
        self._sel = selectors.DefaultSelector()
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sel.register(self._sock, selectors.EVENT_READ)
        self._sock.bind(self._address)
        self._sock.listen(self._backlog)
        self._sock.setblocking(False)
        self._buffer = bytes()
        self.__main_loop()

    def _on_request(self, connection: socket.socket, request: str, args: tuple) -> None:
        return
    
    def broadcast(self, response: str, exclude: tuple = ()) -> None:
        for conn in self.connections:
            if conn in exclude:
                continue
            encoded = response.encode(encoding="utf-8") + self._DELIMITER
            try:
                conn.send(encoded)
            except (ConnectionAbortedError, ConnectionResetError, BrokenPipeError) as exception:
                self._on_connection_disconnected(conn)
                self._sel.unregister(conn)
                self.connections.remove(conn)
                print(f"[Info] {exception.__class__.__name__}: A connection was lost")

    def _on_connection_connected(self, connection: socket.socket) -> None:
        return
    
    def _on_connection_disconnected(self, connection: socket.socket) -> None:
        return # NOTE: connection may be closed

    def __main_loop(self) -> None:
        self._running = True
        print("[Info] Started Server")
        while self._running:
            for key, mask in self._sel.select(timeout=self._NEGATIVE_INF):
                connection = key.fileobj
                if mask & selectors.EVENT_READ:
                    try:
                        data = connection.recv(self._BUFF_SIZE)
                    except OSError:
                        continue
                    if data: # a readable client socket has data.
                        if self._DELIMITER in data: # TODO: if data starts with _DELIMITER, process buffered request
                            head, *rest = data.split(self._DELIMITER)
                            self._buffer += head
                            data = self._buffer.decode()
                            request, *args = data.split(self._ARGUMENT_DELIMITER)
                            self._buffer = bytes()
                            self._on_request(connection, request, list(args))
                            for content in rest[:-1]:
                                data = content.decode()
                                request, *args = data.split(self._ARGUMENT_DELIMITER)
                                self._on_request(connection, request, list(args))
                            self._buffer += rest[-1]
                        else:
                            self._buffer += data
            try:
                connection, address = self._sock.accept()
                self._sel.register(connection, selectors.EVENT_READ)
                self.connections.append(connection)
                print(f"[Info] Client connected [{address}]")
                self._on_connection_connected(connection)
            except BlockingIOError:
                continue


class Server(BaseServer):
    SPAWN_RADIUS_MIN = 50  # minimum
    SPAWN_RADIUS_MAX = 100 # maximum
    REQUEST_PING = "PING:0"
    REQUEST_CREATE = "CREATE:{cls}:x={x}:y={y}"
    RESPONSE_CONNECTION_CONNECTED = "CONNECTED:{cid}" # TODO: ping all connections to update position to current
    RESPONSE_CONNECTION_DISCONNECTED = "DISCONNECTED:{cid}"
    RESPONSE_NEW_PLAYER = "PLAYER_CREATE:{cid}:{x}:{y}"
    RESPONSE_PLAYER_POS = "PLAYER_POS:{cid}:{x}:{y}"
    RESPONSE_MARKER_POS = "MARKER_POS:{cid}:{x}:{y}"

    def __init__(self, host: Union[str, int], port: Union[str, int], backlog: int = 5) -> None:
        self.next_cid = 0
        BaseServer.__init__(self, host, port, backlog)
    
    def _on_connection_connected(self, connection: socket.socket) -> None:
        response = self.RESPONSE_CONNECTION_CONNECTED.format(cid=self.next_cid).encode("utf-8") + self._DELIMITER
        self.next_cid += 1
        connection.send(response) # NOTE: slight chance of crashing. handle it?
        print(f"[Info] Sending CID ({self.next_cid -1}) to new connection")
        # ping other connections
        print(f"[Routine] {len(self.connections)} connections pinged")
        self.broadcast(self.REQUEST_PING, exclude=(connection, ))
        print(f"[Routine] {len(self.connections)} connections remaining")

    def _on_connection_disconnected(self, connection: socket.socket) -> None:
        ... # TODO: ping all connections to see who are still connected

    def _on_request(self, connection: socket.socket, request: str, args: tuple) -> None:
        print("[Request]", request, args)
        if request == "BUG_REPORT":
            date = datetime.datetime.now() # Norwegian date system
            segments = map(str, [date.day, date.month, date.year, date.hour, date.minute, date.second])
            name = "BugReport-{}.{}.{}-{}.{}.{}".format(*segments)
            extension = "txt" # TODO: make bug reports path and extension variables
            path = f"./bug_reports/{name}.{extension}"
            client_info = "Host: {},\nPort: {}".format(*connection.getpeername())
            context = ":".join(args)
            with open(path, "w") as f:
                content = "\n".join([client_info, context])
                f.writelines(content)
            # disconnect temp connection
            self.connections.remove(connection) # TESTME

        elif request == "DISCONNECT":
            cid = args[0]
            response = self.RESPONSE_CONNECTION_DISCONNECTED.format(cid=cid)
            self.broadcast(response, exclude=(connection, ))

        elif request == "CREATE":
            cls, x, y = args
            response = self.REQUEST_CREATE.format(cls=cls, x=x, y=y)
            self.broadcast(response, exclude=(connection, ))

        elif request == "PLAYER_POS":
            cid, x, y = args
            response = self.RESPONSE_PLAYER_POS.format(cid=cid, x=x, y=y)
            self.broadcast(response, exclude=(connection, ))
        
        elif request == "MARKER_POS":
            cid, x, y = args
            response = self.RESPONSE_MARKER_POS.format(cid=cid, x=x, y=y)
            self.broadcast(response, exclude=(connection, ))

        elif request == "PLAYER_JOINED":
            x = random.randint(self.SPAWN_RADIUS_MIN, self.SPAWN_RADIUS_MAX)
            y = random.randint(self.SPAWN_RADIUS_MIN, self.SPAWN_RADIUS_MAX)
            if random.randint(0, 1):
                x = -x
            if random.randint(0, 1):
                y = -y
            cid = self.connections.index(connection)
            response = self.RESPONSE_NEW_PLAYER.format(cid=cid, x=x, y=y)
            self.broadcast(response)
            print(f"[Response] (CID: {cid}) Making new Base at {x}x, {-y}y") # -y because of visual
        
        elif request == "SHELL_LAUNCHED":
            type_name, x, y, tx, ty = args
            extra = f":tx={tx}:ty={ty}"
            response = self.REQUEST_CREATE.format(cls=type_name, x=x, y=y) + extra
            self.broadcast(response, exclude=(connection, ))        


if __name__ == "__main__":
    server = Server("localhost", 7070)
