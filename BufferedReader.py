BUFFER_SIZE = 1024
EMPTY_BYTE_ARRAY = b''


class BufferedReader:
    def __init__(self, sock):
        self.sock = sock
        self.data = EMPTY_BYTE_ARRAY
        self.cursor = 0

    def read_until(self, stop_seq):
        read_bytes = EMPTY_BYTE_ARRAY
        curr_seq = EMPTY_BYTE_ARRAY

        # Read until we have found the stop sequence
        while curr_seq != stop_seq:
            b = self.read_byte()

            if b[0] == stop_seq[len(curr_seq)]:
                # Add the read byte to the current sequence if it matches
                # the next character in the stop sequence
                curr_seq += b
            else:
                # If not, add the current sequence to the read data together
                # with the read byte, and reset it
                read_bytes += curr_seq
                read_bytes += b

                curr_seq = EMPTY_BYTE_ARRAY

        return read_bytes

    def read_bytes(self, num_bytes):
        for i in range(num_bytes):
            self.read_byte()

    def read_byte(self):
        self._buffer()
        b = self.data[self.cursor]
        self.cursor += 1

        return bytes([b])

    @property
    def raw_content(self):
        return self.data[:self.cursor]

    @property
    def content(self):
        return self.raw_content.decode()

    def _buffer(self):
        if self.cursor >= len(self.data):
            self.data += self.sock.recv(BUFFER_SIZE)
