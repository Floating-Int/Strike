from typing import Union
import socket
import selectors


class Client:
    _BUFF_SIZE = 4096
    _DELIMITER = b"$"
    _ARGUMENT_DELIMITER = ":"

    def __init__(self, host: Union[str, int], port: Union[str, int]) -> None:
        self._NEGATIVE_INF = float("-inf")
        self._address = (host, port)
        self._sel = selectors.DefaultSelector()
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sel.register(self._sock, selectors.EVENT_READ)
        self._sock.connect(self._address)
        self._sock.setblocking(False)
        self._buffer = bytes()
    
    def _update_socket(self) -> None:
        # print("Update")
        for key, mask in self._sel.select(timeout=self._NEGATIVE_INF):
            connection = key.fileobj
            if mask & selectors.EVENT_READ:
                # print('  ready to read')
                data = connection.recv(self._BUFF_SIZE)
                if data: # a readable client socket has data.
                    if self._DELIMITER in data:
                        head, *rest = data.split(self._DELIMITER)
                        self._buffer += head
                        data = self._buffer.decode()
                        request, *args = data.split(self._ARGUMENT_DELIMITER)
                        self._buffer = bytes()
                        self._on_request(request, list(args))
                        for content in rest[:-1]:
                            data = content.decode()
                            request, *args = data.split(self._ARGUMENT_DELIMITER)
                            self._on_request(request, list(args))
                        self._buffer += rest[-1]
                    else:
                        self._buffer += data
                    # print('  received {!r}'.format(data))
    
    def _on_request(self, data: str) -> None:
        return
    
    def send(self, request: str) -> None:
        encoded = request.encode(encoding="utf-8") + self._DELIMITER
        self._sock.send(encoded)
