BAD_URL_REDIRECT = b"""HTTP/1.1 301 Moved Permanently
Location: http://www.ida.liu.se/~TDTS04/labs/2011/ass2/error1.html

"""

BAD_CONTENT_REDIRECT = b"""HTTP/1.1 301 Moved Permanently
Location: http://www.ida.liu.se/~TDTS04/labs/2011/ass2/error2.html

"""

BAD_URL_REDIRECT = BAD_URL_REDIRECT.replace(b'\n', b'\r\n')
BAD_CONTENT_REDIRECT = BAD_CONTENT_REDIRECT.replace(b'\n', b'\r\n')

BANNED_WORDS = [
    'SpongeBob',
    'Britney Spears',
    'Britney+Spears',
    'Britney%20Spears',
    'Paris Hilton',
    'Paris+Hilton',
    'Paris%20Hilton',
    'Norrköping',
    'Norrk%C3%B6ping'
]


def contains_bad_word(content_bytes):
    try:
        if isinstance(content_bytes, bytes):
            content = content_bytes.decode().lower()
        else:
            content = content_bytes.lower()
    except:
        return False

    for word in BANNED_WORDS:
        if word.lower() in content:
            return True

    return False


def send_all(s, data):
    sent = 0
    while sent < len(data):
        sent += s.send(data[sent:])
