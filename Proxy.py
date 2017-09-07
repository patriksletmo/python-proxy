import socket
import threading

import sys

from BufferedReader import BufferedReader
from HttpReader import HttpReader
from utils import send_all, contains_bad_word, BAD_URL_REDIRECT, BAD_CONTENT_REDIRECT

MAX_CONNECTION_COUNT = 300
DEFAULT_PORT = 1337


class Proxy:
    def __init__(self, port):
        self.host = '127.0.0.1'
        self.port = port
        self.serversocket = None

    def get_proxy_url(self):
        return 'http://' + self.host + ':' + str(self.port)

    def get_proxies(self):
        """
        Used to setup proxy for automatic testing
        :return: A map between protocols and their respective proxy server
        """
        return {
            'http': self.get_proxy_url()
        }

    def start(self):
        threading.Thread(target=self.runner).start()

    def stop(self):
        self.serversocket.close()

    def runner(self):
        # Open an internet socket for TCP
        self.serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Allow quick re-use to simplify testing
        self.serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Bind the port and start listening for connections
        self.serversocket.bind((self.host, self.port))
        self.serversocket.listen(MAX_CONNECTION_COUNT)

        print('Proxy listening on ' + self.get_proxy_url())

        try:
            while True:
                (clientsocket, address) = self.serversocket.accept()
                Proxy.write_response_async(clientsocket)
        except:
            pass

    @staticmethod
    def write_response_async(clientsocket):
        """
        Starts a new thread to handle the request, in order to increase performance.
        :param clientsocket: The socket connecting the proxy client with our proxy server
        """

        threading.Thread(target=Proxy.write_response,
                         args={clientsocket}).start()

    @staticmethod
    def write_response(clientsocket):
        # Read request from proxy client
        request = HttpReader(BufferedReader(clientsocket))
        request.read()

        if contains_bad_word(request.raw_content) and not contains_bad_word(request.headers.get('Referer')):
            # Filter bad urls but do not put us in an endless redirection loop ^
            send_all(clientsocket, BAD_URL_REDIRECT)
        else:
            # Remove the host from the requested url to ensure that all web servers can handle the request
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
                # Redirect to the error page if trying to access bad content
                send_all(clientsocket, BAD_CONTENT_REDIRECT)
            else:
                # Forward the response to the proxy client
                send_all(clientsocket, response.raw_content)

            # Close web server connection
            websocket.close()

        # Close proxy client connection
        clientsocket.close()


if __name__ == '__main__':
    port = DEFAULT_PORT
    if len(sys.argv) > 1:
        port = int(sys.argv[1])

    proxy = Proxy(port)
    proxy.start()
