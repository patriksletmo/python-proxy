from unittest import TestCase
import requests

from Proxy import Proxy

SIMPLE_TEXT_FILE = 'http://www.ida.liu.se/~TDTS04/labs/2011/ass2/goodtest1.txt'
SIMPLE_HTML_FILE = 'http://www.ida.liu.se/~TDTS04/labs/2011/ass2/goodtest2.html'

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
