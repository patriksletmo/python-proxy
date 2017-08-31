import socket

SOME_CONTENT = """
HTTP/1.1 200 OK
Date: Thu, 31 Aug 2017 07:14:03 GMT
Server: Apache/2.4.6 (CentOS) OpenSSL/1.0.1e-fips PHP/5.4.16 mod_perl/2.0.10 Perl/v5.16.3
Last-Modified: Thu, 31 Aug 2017 05:59:01 GMT
ETag: "173-5580657531af7"
Accept-Ranges: bytes
Content-Length: 371
Keep-Alive: timeout=5, max=100
Connection: Keep-Alive
Content-Type: text/html; charset=UTF-8


<html>

Congratulations again!  Now you've downloaded the file lab2-2.html. <br>
This file's last modification date will not change.  <p>
Thus  if you download this multiple times on your browser, a complete copy <br>
will only be sent once by the server due to the inclusion of the IN-MODIFIED-SINCE<br>
field in your browser's HTTP GET request to the server.

</html>
"""


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
        # Open an internet socket for TCP
        serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serversocket.bind((self.host, self.port))
        serversocket.listen(5)  # Max 5 concurrent connections

        while True:
            # accept connections from outside
            (clientsocket, address) = serversocket.accept()
            # now do something with the clientsocket
            # in this case, we'll pretend this is a threaded server
            ct = client_thread(clientsocket)
            ct.run()
