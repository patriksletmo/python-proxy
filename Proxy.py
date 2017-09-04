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
        #self.serversocket.shutdown(socket.SHUT_RDWR)
        self.serversocket.close()

    def runner(self):
        # Open an internet socket for TCP
        self.serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.serversocket.bind((self.host, self.port))
        self.serversocket.listen(5)  # Max 5 concurrent connections

        try:
            while True:
                # accept connections from outside
                (clientsocket, address) = self.serversocket.accept()
                # now do something with the clientsocket
                # in this case, we'll pretend this is a threaded server
                # ct = client_thread(clientsocket)
                # ct.run()
                print('New connection from ' + str(address))
                #self.write_dummy_response(clientsocket)
                self.write_response(clientsocket)
        except ConnectionAbortedError:
            pass
        except OSError:
            pass

    def write_dummy_response(self, clientsocket):
        clientsocket.send(SOME_CONTENT)

    def write_response(self, clientsocket):
        request_content = clientsocket.recv(1024).decode()
        hostname = self.extract_header(request_content, 'Host')

        websocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        websocket.connect((hostname, 80))

        websocket.send(bytes(request_content, 'UTF-8'))
        response_content = websocket.recv(1024)
        clientsocket.send(response_content)

        websocket.shutdown(socket.SHUT_RDWR)
        websocket.close()

        clientsocket.close()

    def extract_header(self, content, name):
        full_name = '\r\n' + name + ':'
        header_name_start = content.index(full_name)
        header_value_start = header_name_start + len(full_name)
        header_value_stop = content.index('\r\n', header_value_start)

        return content[header_value_start:header_value_stop].strip()
