#!/usr/bin/env python
import sys
import StringIO
from PIL import Image, ImageOps
import images2gif 
from pymemcache.client.base import Client

# http://stackoverflow.com/questions/19149643/error-in-images2gif-py-with-globalpalette
# change palettes.append( getheader(im)[1] ) to palettes.append(im.palette.getdata()[1]) in images2gif.py

client = Client(('127.0.0.1', 11211))
images = []
size = 256, 192
timespace = 10

try:
	result = client.get('curno')
	if result :
		curno = int(result)
		for i in range((curno - timespace), curno):
			data = client.get(str(i))
			if data:
				im = Image.open(StringIO.StringIO(data))
				imresized = ImageOps.fit(im, size, Image.ANTIALIAS)
				images.append(imresized)

		filename = "my_gif.GIF"
		images2gif.writeGif(filename, images, duration=0.2)

except Exception, e:
	print e.__doc__
	print e.message      
	sys.exit(1)

except KeyboardInterrupt:
	sys.exit(1)