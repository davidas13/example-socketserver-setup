import sys

from socket_setup.socket_setup import SetupClient

if __name__ == "__main__":
    message = sys.argv[1]
    client = SetupClient()
    client.send(str(message))
    print(client.receive())
