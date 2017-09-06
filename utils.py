def send_all(s, data):
    sent = 0
    while sent < len(data):
        sent += s.send(data[sent:])
