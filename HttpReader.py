from Headers import Headers

NEWLINE = b'\r\n'
SECTION_STOP = NEWLINE + NEWLINE


class HttpReader:
    def __init__(self, reader):
        self.reader = reader
        self.headers = None

    def read(self):
        self.headers = Headers(self.reader.read_until(SECTION_STOP))

        if self.headers.get_token('Transfer-Encoding') == 'chunked':
            self._read_chunked()
        else:
            self._read_normal()

    @property
    def raw_content(self):
        return self.reader.raw_content

    @property
    def content(self):
        return self.raw_content.decode()

    def _read_chunked(self):
        while True:
            chunk_size = self._read_chunk_size()
            if chunk_size > 0:
                # Read chunk data plus the trailing newline
                self.reader.read_bytes(chunk_size)
                self.reader.read_bytes(len(NEWLINE))
            else:
                break

        # Chunked encoding is terminated by a final newline
        self.reader.read_bytes(len(NEWLINE))

    def _read_normal(self):
        content_length_str = self.headers.get('Content-Length')

        if content_length_str != '':
            self.reader.read_bytes(int(content_length_str))

    def _read_chunk_size(self):
        size_bytes = self.reader.read_until(NEWLINE)
        size_hex = size_bytes.decode()

        return int(size_hex, 16)
