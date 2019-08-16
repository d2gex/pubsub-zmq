from os.path import join
from pathlib import Path

path = Path(__file__).resolve()
ROOT = path.parents[1]
TEST = join(ROOT, 'tests')

TCP_CLIENT_ADDRESS = "127.0.0.1"
TCP_SERVER_ADDRESS = "127.0.0.1"

TCP_PORT = "5556"
TCP_PROTOCOL = "tcp://"

TCP_CONNECT_URL_SOCKET = TCP_PROTOCOL + TCP_CLIENT_ADDRESS + ":" + TCP_PORT
TCP_BIND_URL_SOCKET = TCP_PROTOCOL + TCP_SERVER_ADDRESS + ":" + TCP_PORT
