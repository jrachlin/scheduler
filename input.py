import socket
import logging
import socketserver
import multiprocessing as mp


message_queue = mp.Queue()
HOST = "localhost"
logger = logging.getLogger(__name__)


class UserInputHandler(socketserver.BaseRequestHandler):
    """
    The request handler class for our user input server.
    """
    message_queue = message_queue

    def handle(self):
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(1024)
        # Echo request to acknowledge
        self.request.sendall(self.data)
        message_queue.put(self.data.decode('utf-8'))

def initialize_ui_listener():
    logger.info('Creating UI Listener')
    server = socketserver.TCPServer((HOST, 0), UserInputHandler)
    port = server.server_address[1]
    return server, port

def launch_ui_listener(server):
    logger.info('Launching UI Listener')
    with server:
        server.serve_forever()

def send_user_input(data, port):

    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s |> %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    # Create a socket (SOCK_STREAM means a TCP socket)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        # Connect to server and send data
        sock.connect((HOST, port))
        data = data.encode('utf-8')
        sock.sendall(data)

        # Receive data from the server and shut down
        received = sock.recv(1024).decode('utf-8')
    logger.info('Instruction Sent: [%s]', received)
