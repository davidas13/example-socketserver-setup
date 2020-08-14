from socket_setup.socket_setup import SetupServer, SetupServerHandler


class ServerHandler(SetupServerHandler):
    def handle(self) -> None:
        message_res = self.receive().upper()
        self.send(message_res)
        super(ServerHandler, self).handle()


if __name__ == "__main__":
    server = SetupServer(handler_class=ServerHandler)
    server.run()
