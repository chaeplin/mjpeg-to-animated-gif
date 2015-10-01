#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = 'CHAEPIL LIM <chaeplin()gmail.com>'
__copyright__ = 'Copyright 2015 CHAEPIL LIM'
__license__   = """Eclipse Public License - v 1.0 (http://www.eclipse.org/legal/epl-v10.html)"""

    
HAVE_SLACK=True
try:
    from slacker import Slacker
    import sys
    import os
    import StringIO
    import images2gif
    import datetime    
    from PIL import Image, ImageOps
    from pymemcache.client.base import Client

except ImportError:
    HAVE_SLACK=False

"""
[config:slackgif]
token = 'xxxx-1234567890-1234567890-1234567890-1234a1'
targets = {
              #channel_id,  size_x, size_y, timespan, dir_to_save
    'mychannel' : [ 'channel_id',   256,  192,  10, '/home/nfs/webcam' ],
  }

from http://stackoverflow.com/questions/19149643/error-in-images2gif-py-with-globalpalette
change palettes.append( getheader(im)[1] ) to palettes.append(im.palette.getdata()[1]) in images2gif.py  
"""

def plugin(srv, item):

    srv.logging.debug("*** MODULE=%s: service=%s, target=%s", __file__, item.service, item.target)

    if HAVE_SLACK == False:
        srv.logging.error("slacker module missing")
        return False

    token = item.config.get('token')
    if token is None:
        srv.logging.error("No token found for slack")
        return False

    try:
        channel_id, size_x, size_y, timespan, dir_to_save = item.addrs

    except:
        srv.logging.error("Incorrect target configuration")
        return False

    # make animated gif, save to local disk, upload to slack channel

    client = Client(('127.0.0.1', 11211))
    images_original = []
    images_resized  = []
    size = size_x, size_y

    cur_month = datetime.datetime.now().strftime("%Y%m")
    cur_time = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")

    cur_dir = dir_to_save + "/" + cur_month
    if not os.path.exists(cur_dir):
        os.makedirs(cur_dir)

    cur_img_original = cur_dir + "/" + cur_time + ".gif"
    cur_img_resized  = cur_dir + "/" + cur_time + "_s.gif"

    # make a gif file
    try:
        result = client.get('curno')
        if result :
            curno = int(result)
            for i in range((curno - timespan), curno):
                data = client.get(str(i))
                if data:
                    im = Image.open(StringIO.StringIO(data))
                    images_original.append(im)
                    imresized = ImageOps.fit(im, size, Image.ANTIALIAS)
                    images_resized.append(imresized)

            if len(images_original) > 0:
                images2gif.writeGif(cur_img_original, images_original, duration=0.2)
                images2gif.writeGif(cur_img_resized, images_resized, duration=0.2)


    except Exception, e:
        srv.logging.warning("Cannot make a gif: %s" % (str(e)))
        return False

    # upload to slack
    try:
        slack = Slacker(token)
        if os.path.isfile(cur_img_resized):
            slack.files.upload(cur_img_resized, channels=channel_id)

    except Exception, e:
        srv.logging.warning("Cannot post to slack: %s" % (str(e)))
        return False

    return True


