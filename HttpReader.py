from Headers import Headers

NEWLINE = b'\r\n'
SECTION_STOP = NEWLINE + NEWLINE


class HttpReader:
    """
    Reads an HTTP response from a BufferedReader
    """

    def __init__(self, reader):
        self.reader = reader
        self.headers = None

    def read(self):
        # Parse the headers string into a Headers structure
        self.headers = Headers(self.reader.read_until(SECTION_STOP))

        # Read the rest of the content depending on the transfer encoding
        if self.headers.get_token('Transfer-Encoding') == 'chunked':
            self._read_chunked()
        else:
            self._read_normal()

    @property
    def raw_content(self):
        """
        Returns the read content as a byte array
        """

        return self.reader.raw_content

    @property
    def content(self):
        """
        Returns the read content as a string
        """

        return self.raw_content.decode()

    def _read_chunked(self):
        # For data format, please see https://en.wikipedia.org/wiki/Chunked_transfer_encoding

        while True:
            chunk_size = self._read_chunk_size()

            # Read chunk data plus the trailing newline
            self.reader.read_bytes(chunk_size)
            self.reader.read_bytes(len(NEWLINE))

            if chunk_size == 0:
                # Chunked data is terminated by a chunk of size 0
                break

    def _read_normal(self):
        content_length_str = self.headers.get('Content-Length')

        if content_length_str != '':
            self.reader.read_bytes(int(content_length_str))

    def _read_chunk_size(self):
        size_bytes = self.reader.read_until(NEWLINE)
        size_hex = size_bytes.decode()

        return int(size_hex, 16)
