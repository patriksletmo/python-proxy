import socket
import threading


HTML_CONTENT = b'\nThis is a plain text file with no bad words in it.\n\nYour Web browser should be able to display this page just fine.\n\n\n'

SOME_CONTENT = b"""HTTP/1.1 200 OK
Date: Thu, 31 Aug 2017 07:14:03 GMT
Server: Apache/2.4.6 (CentOS) OpenSSL/1.0.1e-fips PHP/5.4.16 mod_perl/2.0.10 Perl/v5.16.3
Last-Modified: Thu, 31 Aug 2017 05:59:01 GMT
ETag: "173-5580657531af7"
Accept-Ranges: bytes
Content-Length: """ + bytes(str(len(HTML_CONTENT)), 'UTF-8') + b"""
Keep-Alive: timeout=5, max=100
Connection: Keep-Alive
Content-Type: text/html; charset=UTF-8

"""

SOME_CONTENT = SOME_CONTENT.replace(b'\n', b'\r\n') + HTML_CONTENT


class Proxy:
    def __init__(self):
        self.host = '127.0.0.1'
        self.port = 1337

    def get_proxy_url(self):
        return 'http://' + self.host + ':' + str(self.port)

    def get_proxies(self):
        return {
            'http': self.get_proxy_url()
        }

    def start(self):
        threading.Thread(target=self.runner).start()

    def runner(self):
        # Open an internet socket for TCP
        serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serversocket.bind((self.host, self.port))
        serversocket.listen(5)  # Max 5 concurrent connections

        while True:
            # accept connections from outside
            (clientsocket, address) = serversocket.accept()
            # now do something with the clientsocket
            # in this case, we'll pretend this is a threaded server
            #ct = client_thread(clientsocket)
            #ct.run()
            print('New connection from ' + str(address))
            self.write_dummy_response(clientsocket)

    def write_dummy_response(self, clientsocket):
        clientsocket.send(SOME_CONTENT)
