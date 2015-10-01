#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = 'Jan-Piet Mens <jpmens()gmail.com>'
__copyright__ = 'Copyright 2014 Jan-Piet Mens'
__license__   = """Eclipse Public License - v 1.0 (http://www.eclipse.org/legal/epl-v10.html)"""

HAVE_SLACK=True
try:
    from slacker import Slacker
    import sys
    import StringIO
    from PIL import Image, ImageOps
    import images2gif 
    from pymemcache.client.base import Client
    import datetime

except ImportError:
    HAVE_SLACK=False

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
        channel, username, icon = item.addrs
    except:
        srv.logging.error("Incorrect target configuration")
        return False

    # If the incoming payload has been transformed, use that,
    # else the original payload
    text = item.message

    if channel == "#raspberrypi" :

        client = Client(('127.0.0.1', 11211))
        images = []
        size = 256, 192
        timespace = 10

        cur_month = datetime.datetime.now().strftime("%Y%m")
        cur_time = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")

        imagefiletoupload = "/home/nfs/webcam/" + cur_month + "/" + cur_time + ".gif"

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

                images2gif.writeGif(imagefiletoupload, images, duration=0.2)

        except Exception, e:
            srv.logging.warning("Cannot make gif: %s" % (str(e)))
            return False

        try:
            slack = Slacker(token)
            slack.files.upload(imagefiletoupload, channels='channel_to_upload')

        except Exception, e:
            srv.logging.warning("Cannot post to slack: %s" % (str(e)))
            return False

    return True


