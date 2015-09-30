#!/usr/bin/env python
import sys
import time
import urllib2
from PIL import Image
from pymemcache.client.base import Client

client = Client(('127.0.0.1', 11211))
url = "http://127.0.0.1:5080/index1.jpg"
i = 0

try:
    while True:
        try:
            input = urllib2.urlopen(url)
            input.readline(); input.readline()
            content_length = int(input.readline().split(": ")[1].strip())
            input.readline(); input.readline()
            data = input.read(content_length)
            client.set(str(i), data, 30)
            client.set('curno', i)
    
            i = i + 1 
            time.sleep(0.7)
    
        except Exception, e:
            print e.__doc__
            print e.message      
            sys.exit(1)

except KeyboardInterrupt:
    sys.exit(1)