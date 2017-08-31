class Proxy:
    def __init__(self):
        self.port = 1337

    def get_proxy_url(self):
        return 'http://127.0.0.1:' + str(self.port)

    def get_proxies(self):
        return {
            'http': self.get_proxy_url()
        }
