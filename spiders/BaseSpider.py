import re
import urllib
import threading
import Queue

class BaseSpider(threading.Thread):
    
    def __init__(self):
        threading.Thread.__init__(self)
        
    def run