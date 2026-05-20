from django.test import TestCase
import requests
from bs4 import BeautifulSoup

# Create your tests here.
class Test():
    def __init__(self, test):
        self.test = test
        if test == "posts_POST":
            self.posts_POST()
    def posts_POST(self):
        content = requests.get(url="http://127.0.0.1:8000/posts/create").content


