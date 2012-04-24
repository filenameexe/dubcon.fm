#!/usr/bin/env python

import cgi
import re

import cgitb
cgitb.enable()

form = cgi.FieldStorage()

def fb_authentication():
    auth_url = """https://www.facebook.com/dialog/oauth?
                    client_id=224721717634630
                    &redirect_uri=http://23.22.47.161/dubcon.fm/fb_authentication.py
                    &response_type=token
                    &scope=user_groups"""
    auth_url = re.sub('\n', '', auth_url)
    auth_url = re.sub(' ', '', auth_url)

    print """Content-Type: text/html

    <script>
        if (window.location.hash){
            window.location='fb_authentication.py?' + window.location.hash.substring(1);
        } else {
            window.location="%s"
        }
    </script>
    """ % auth_url


if not form:
    fb_authentication()
else:
    # print "Content-Type: text/html\n"
    print "Location: radio.py?access_token=%s\n" % form.getvalue('access_token')
