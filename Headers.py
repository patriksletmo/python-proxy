class Headers:
    """
    Helper used to extract header values from their string representation
    """

    def __init__(self, raw_data):
        self.data = raw_data.decode() + '\r\n'

    def get(self, name):
        """
        Returns the value of the header with the given name, or an empty string if not found
        """

        try:
            content = self.data.lower()
            name = name.lower()

            full_name = '\r\n' + name + ':'
            header_name_start = content.index(full_name)
            header_value_start = header_name_start + len(full_name)
            header_value_stop = content.index('\r\n', header_value_start)

            return self.data[header_value_start:header_value_stop].strip()
        except ValueError:
            return ''

    def get_token(self, name):
        """
        Returns the value of the header with the given name, but in a format suitable for comparing it with a constant
        :return: The lower characters of the header value
        """

        return self.get(name).lower()
