import socket
import threading

import sys

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


def send_all(s, data):
    sent = 0
    while sent < len(data):
        sent += s.send(data[sent:])


def recv_all(s):
    first_received = s.recv(1024)

    try:
        print('\nResponse:')
        print(first_received.decode())
        sys.stdout.flush()
    except:
        print('<chunked>')

    headers_end = first_received.index(b'\r\n\r\n')
    headers = first_received[:headers_end].decode()
    transfer_encoding = extract_header(headers, 'Transfer-Encoding')
    if transfer_encoding.lower() == 'chunked':
        return recv_chunked(s, first_received, headers_end)
    else:
        return recv_normal(s, first_received, headers)


def recv_size(s, size):
    data = b''
    while len(data) < size:
        remaining_size = size - len(data)
        data += s.recv(min(remaining_size, 1024))

    return data


def read_chunk_size(s):
    header_data = b''
    header_data += recv_size(s, 2)

    data = b''
    while True:
        c = recv_size(s, 1)
        if c == b'\r':
            header_data += c
            header_data += recv_size(s, 1)
            break
        else:
            header_data += c
            data += c

    chunk_size_hex = data.decode()
    return int(chunk_size_hex, 16), header_data


def read_received_chunks(s, data):
    new_data = b''

    chunk_size_stop = data.index(b'\r\n', 2)
    chunk_size_bytes = data[2:chunk_size_stop]
    chunk_size_hex = chunk_size_bytes.decode()
    chunk_size = int(chunk_size_hex, 16)

    chunk_header_size = chunk_size_stop + 2
    chunk_header_data = data[:chunk_header_size]
    remaining_data = data[chunk_header_size:]

    chunk_data = remaining_data[:min(chunk_size, len(remaining_data))]

    new_data += chunk_header_data
    new_data += chunk_data

    if len(chunk_data) < chunk_size:
        # Final chunk data must be read from stream
        new_data += recv_size(s, chunk_size - len(chunk_data))
    elif len(chunk_data) < len(remaining_data):
        # More chunks must be read from the already received content
        new_data += read_received_chunks(s, remaining_data[len(chunk_data):])

    return new_data


def recv_chunked(s, first_received, headers_end):
    data = b''

    chunk_size_start = headers_end + 2

    data += first_received[:chunk_size_start]
    data += read_received_chunks(s, first_received[chunk_size_start:])

    while True:
        chunk_size, chunk_header_data = read_chunk_size(s)

        data += chunk_header_data
        if chunk_size > 0:
            data += recv_size(s, chunk_size)
        else:
            break

    data += b'\r\n'

    return data


def recv_normal(s, first_received, headers):
    data = first_received

    content_length_str = extract_header(headers, 'Content-Length')
    if content_length_str.lower() != '':
        content_start = len(headers) + 4
        content_length = int(content_length_str)

        if content_length > len(first_received) - content_start:
            # There is more content to read
            data += recv_size(s, content_length - (len(first_received) - content_start))

    return data


def extract_header(original_content, name):
    try:
        content = original_content.lower()
        name = name.lower()

        full_name = '\r\n' + name + ':'
        header_name_start = content.index(full_name)
        header_value_start = header_name_start + len(full_name)
        header_value_stop = content.index('\r\n', header_value_start)

        return original_content[header_value_start:header_value_stop].strip()
    except:
        return ''


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
        self.serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.serversocket.bind((self.host, self.port))
        self.serversocket.listen(5)  # Max 5 concurrent connections

        try:
            while True:
                (clientsocket, address) = self.serversocket.accept()
                self.write_response_async(clientsocket)
        except ConnectionAbortedError:
            pass
        except OSError:
            pass

    def write_response_async(self, clientsocket):
        threading.Thread(target=self.write_response,
                         args={clientsocket}).start()

    def write_response(self, clientsocket):
        print('\nNew request:')
        sys.stdout.flush()

        request_content = clientsocket.recv(1024).decode()
        hostname = extract_header(request_content, 'Host')

        request_content = request_content.replace('http://' + hostname, '', 1)

        print(request_content)
        sys.stdout.flush()

        websocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        websocket.connect((hostname, 80))

        websocket.send(bytes(request_content, 'UTF-8'))
        response_content = recv_all(websocket)

        clientsocket.send(response_content)

        websocket.close()

        clientsocket.close()
