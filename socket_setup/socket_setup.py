import codecs
import logging
import os
import pickle
import socket
import sys
import threading
from socketserver import TCPServer, BaseRequestHandler
from typing import Tuple, Any, Dict, Type, Union, Optional

sys.dont_write_bytecode = True

BASE_PATH: str = os.getcwd()
SERVER_SETUP_FILE: str = os.path.join(BASE_PATH, "server.setup")

logging.basicConfig(level=logging.DEBUG, format="[%(levelname)s] [%(name)s] %(asctime)s - %(message)s")


class SetupServerHandler(BaseRequestHandler):
    def __init__(self, request: socket.socket, client_address: Tuple[str, int], server: TCPServer):
        self.logger = logging.getLogger("ServerHandler")
        self.request: socket.socket = request
        self.client_address: Tuple[str, int] = client_address
        self.server: TCPServer = server
        super(SetupServerHandler, self).__init__(request, client_address, server)

    def handle(self) -> None:
        self.logger.info(f"Handle Request: {self.receive()}")
        super(SetupServerHandler, self).handle()

    def receive(self) -> Union[str, int]:
        self.logger.debug(f"Receive Message from: {self.client_address}")
        data = self.request.recv(1024)
        return codecs.decode(data)

    def send(self, msg) -> None:
        self.logger.debug(f"Send Message to: {self.client_address}")
        self.request.send(codecs.encode(msg))


class SetupServer(TCPServer):
    def __init__(self, host: Union[str, None] = None, port: Union[int, None] = None,
                 handler_class: Optional[Type[BaseRequestHandler]] = None) -> None:
        self.__hostname = socket.gethostname()
        self.__host: str = host if host else socket.gethostbyname(self.__hostname)
        self.__port: int = port if port else 8013
        self.__address: Tuple[str, int] = (self.__host, self.__port)
        self.__handler_class: Type[BaseRequestHandler] = handler_class if handler_class else SetupServerHandler
        self.logger = logging.getLogger(f"Server {self.__hostname}")

        super(SetupServer, self).__init__(self.__address, self.__handler_class)
        self.setup()

    @property
    def host(self) -> str:
        return self.__host

    @property
    def port(self) -> int:
        return self.__port

    @property
    def address(self) -> Tuple[str, int]:
        return self.__address

    def run(self) -> None:
        thread = threading.Thread(target=self.serve_forever)
        thread.start()

    def setup(self, save_to: Union[str, None] = None) -> None:
        setup_data: Dict[str, Any] = {"host": self.__host, "port": self.__port, "address": self.__address}
        setup_file = save_to if save_to else SERVER_SETUP_FILE
        with open(setup_file, "wb") as fd:
            pickle.dump(setup_data, fd)

    def server_activate(self) -> None:
        self.logger.info(f"Server Activate: {self.server_address}")
        super(SetupServer, self).server_activate()

    def serve_forever(self, **kwargs) -> None:
        self.logger.debug("Waiting Request")
        self.logger.info("Press [Ctrl-C] to Quit")
        super(SetupServer, self).serve_forever(**kwargs)

    def server_close(self) -> None:
        self.logger.info("Server Close")
        super(SetupServer, self).server_close()


class SetupClient(socket.socket):
    def __init__(self, family: int = socket.AF_INET, type: int = socket.SOCK_STREAM, **kwargs) -> None:
        super(SetupClient, self).__init__(family, type, **kwargs)
        self.__hostname = socket.gethostname()
        self.logger = logging.getLogger(f"Client {self.__hostname}")

        self.setup()

    def setup(self, load_from: Union[str, None] = None):
        setup_file: str = load_from if load_from else SERVER_SETUP_FILE
        if not os.path.exists(setup_file):
            raise self.logger.exception("Cannot Found server.setup file!")

        with open(setup_file, "rb") as fd:
            setup_data: Dict[str, Any] = pickle.load(fd)
            self.connect(setup_data["address"])

    def receive(self) -> Union[str, int]:
        self.logger.debug("Receive Message")
        res = self.recv(1024)
        return codecs.decode(res)

    def send(self, msg: str, **kwargs) -> None:
        self.logger.debug("Send Message")
        data = codecs.encode(msg)
        super(SetupClient, self).send(data, **kwargs)
