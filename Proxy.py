import socket
import threading

from BufferedReader import BufferedReader
from HttpReader import HttpReader
from utils import send_all, contains_bad_word, BAD_URL_REDIRECT, \
    BAD_CONTENT_REDIRECT

MAX_CONNECTION_COUNT = 5


class Proxy:
    def __init__(self):
        self.host = '127.0.0.1'
        self.port = 1337
        self.serversocket = None

    def get_proxy_url(self):
        return 'http://' + self.host + ':' + str(self.port)

    def get_proxies(self):
        return {
            'http': self.get_proxy_url()
        }

    def start(self):
        threading.Thread(target=self.runner).start()

    def stop(self):
        # self.serversocket.shutdown(socket.SHUT_RDWR)
        self.serversocket.close()

    def runner(self):
        # Open an internet socket for TCP
        self.serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Allow quick re-use to simplify testing
        self.serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Bind the port and start listening for connections
        self.serversocket.bind((self.host, self.port))
        self.serversocket.listen(MAX_CONNECTION_COUNT)

        try:
            while True:
                (clientsocket, address) = self.serversocket.accept()
                Proxy.write_response_async(clientsocket)
        except ConnectionAbortedError:
            pass
        except OSError:
            pass

    @staticmethod
    def write_response_async(clientsocket):
        threading.Thread(target=Proxy.write_response,
                         args={clientsocket}).start()

    @staticmethod
    def write_response(clientsocket):
        # Read request from proxy client
        request = HttpReader(BufferedReader(clientsocket))
        request.read()

        if contains_bad_word(request.raw_content):
            send_all(clientsocket, BAD_URL_REDIRECT)
        else:
            # Remove the host from the requested url
            hostname = request.headers.get('Host')
            request_content = request.content
            request_content = request_content.replace('http://' + hostname, '', 1)

            # Connect to the actual web server and send the request
            websocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            websocket.connect((hostname, 80))
            send_all(websocket, bytes(request_content, 'UTF-8'))

            # Read response from the web server
            response = HttpReader(BufferedReader(websocket))
            response.read()

            if contains_bad_word(response.raw_content):
                send_all(clientsocket, BAD_CONTENT_REDIRECT)
            else:
                # Forward the response to the proxy client
                send_all(clientsocket, response.raw_content)

            # Close web server connection
            websocket.close()

        # Close proxy client connection
        clientsocket.close()
