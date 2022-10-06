import traceback
import socket
import io


class BugReport:
    _DELIMITER = b"$"
    _REQUEST_BUG_REPORT = "BUG_REPORT:{context}"

    def __init__(self, address) -> None:
        self._addresss = address
        self._fd = io.StringIO()
        traceback.print_exc(file=self._fd)
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    def submit(self) -> None: # NOTE: an error should not occure here
        # create request
        context = self._fd.getvalue()
        request = self._REQUEST_BUG_REPORT.format(context=context).encode("utf-8") + self._DELIMITER
        # do transfer
        self._sock.connect(self._addresss)
        self._sock.send(request)
        self._sock.close()
        # print("REQUEST:")
        # print(request)
    
    def print_report(self) -> None:
        context = self._fd.getvalue()
        print(f'BugReport("\n', context, '")', sep="")
