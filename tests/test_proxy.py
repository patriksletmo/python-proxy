from unittest import TestCase
import requests

from Proxy import Proxy

SIMPLE_TEXT_FILE = 'http://www.ida.liu.se/~TDTS04/labs/2011/ass2/goodtest1.txt'
SIMPLE_HTML_FILE = 'http://www.ida.liu.se/~TDTS04/labs/2011/ass2/goodtest2.html'
BAD_URL_FILE = 'http://www.ida.liu.se/~TDTS04/labs/2011/ass2/SpongeBob.html'
BAD_CONTENT_FILE = 'http://www.ida.liu.se/~TDTS04/labs/2011/ass2/badtest1.html'

SIMPLE_TEXT_CONTENT = b'\nThis is a plain text file with no bad words in it.\n\nYour Web browser should be able to display this page just fine.\n\n\n'
SIMPLE_HTML_CONTENT = b'<html>\n\n<title>\nGood HTML File Test for CPSC 441 Assignment 1\n</title>\n\n<body>\n<p>\nThis is a simple HTML file with no bad words in it.\n</p>\n\n<p>\nYour Web browser should be able to display this page just fine.\n</p>\n\n</body>\n\n</html>\n\n\n'


proxy = Proxy()


class TestProxy(TestCase):
    @classmethod
    def setUpClass(cls):
        proxy.start()

    @classmethod
    def tearDownClass(cls):
        proxy.stop()

    def test_simple_text_file(self):
        response = requests.get(SIMPLE_TEXT_FILE, proxies=proxy.get_proxies())
        self.assertEqual(SIMPLE_TEXT_CONTENT, response.content)

    def test_simple_html_file(self):
        response = requests.get(SIMPLE_HTML_FILE, proxies=proxy.get_proxies())
        self.assertEqual(SIMPLE_HTML_CONTENT, response.content)

    def test_redirect(self):
        response = requests.get('http://aftonbladet.se',
                                proxies=proxy.get_proxies())
        self.assertEqual(200, response.status_code)

    def test_large_site(self):
        response = requests.get('http://www.aftonbladet.se', proxies=proxy.get_proxies())
        self.assertEqual(200, response.status_code)

    def test_user_sites(self):
        self.assertEqual(200, requests.get('http://www.stackoverflow.com/', proxies=proxy.get_proxies()).status_code)
        self.assertEqual(200, requests.get('http://www.svd.se/', proxies=proxy.get_proxies()).status_code)
        self.assertEqual(200, requests.get('http://www.liu.se/', proxies=proxy.get_proxies()).status_code)
        self.assertEqual(200, requests.get('http://www.qz.com/', proxies=proxy.get_proxies()).status_code)
        self.assertEqual(200, requests.get('http://www.bbc.com/', proxies=proxy.get_proxies()).status_code)

    def test_https_redirect(self):
        response = requests.get('http://baljan.org', proxies=proxy.get_proxies())
        self.assertEqual(200, response.status_code)

    def test_bad_url(self):
        response = requests.get(BAD_URL_FILE, proxies=proxy.get_proxies())
        self.assertEqual('http://www.ida.liu.se/~TDTS04/labs/2011/ass2/error1.html', response.url)

    def test_bad_content(self):
        response = requests.get(BAD_CONTENT_FILE, proxies=proxy.get_proxies())
        self.assertEqual('http://www.ida.liu.se/~TDTS04/labs/2011/ass2/error2.html', response.url)
