#!/usr/bin/env python

# Import Python Classes
import cgi
import os
import sys
import urllib2

import ConfigParser

try:
    import simplejson as json
except:
    import json


# Global variables
form = cgi.FieldStorage()
graph_url = 'https://graph.facebook.com/'
feed_id = 136242783083472

# Debug statements
import cgitb
cgitb.enable()
DEBUG = True

def pretty_print_json(json_input):
    '''Helper method for inspecting json in the command line.'''
    print json.dumps(json_input, sort_keys = True, indent = 4)



def curl_to_json(URL):
    '''Grab a website's data and convert it to json.'''

    request = urllib2.Request(URL)
    try:
        response = urllib2.urlopen(request).read()
    except urllib2.HTTPError:
        return
    return json.loads(response)

def get_fb_feed():
    '''Get the Facebook feed using a facebook access token and feed id.'''
    radio_feed_url = '{0}{1}/feed?access_token={2}&format=json&limit=25'.format(
                            graph_url,
                            feed_id,
                            form.getvalue('access_token'))

    if DEBUG:
        print 'Curl URL:',radio_feed_url
    return curl_to_json(radio_feed_url)

def extract_youtube_links(fb_feed):
    '''Get all youtube links from the returned fb feed.'''

    # Create an empty list
    youtube_links = []

    # Loop through the fb_feed's data section. Call each item 'post'.
    for post in fb_feed['data']:

        # Inspect each post
        # print pretty_print_json(post) # <-- this is currently commented out

        # Check if the key 'link' exists in this post and that
        # The substring 'youtube.com' exists in post['link']
        if 'link' in post and 'youtube.com' in post['link']:
            # If so, add this to the list
            youtube_links.append(post['link'])

    # Return this list
    return youtube_links

def extract_youtube_ids(youtube_links):
    '''Loop through the passed array and only get the ID portion. Return a list of IDs.'''

    # To write
    # Do this first, much like extract_youtube_links, but perhaps with string finds or regex.
    # Strings are probably easier
    # http://docs.python.org/tutorial/datastructures.html#list-comprehensions
    # http://docs.python.org/library/string.html
    # http://docs.python.org/library/re.html
    pass

def construct_youtube_embed(youtube_ids):
    '''Write the full html embedded code.'''

    # To write
    # Go to mixfeed.me and right click and view the source.
    # Towards the bottom you'll see how playlists are formed.
    # Print this out via python and save it into an html file.
    # If this method works correctly, then when you open your html page
    # in a brower you should get a playlist of these songs.

    # Using %s or .format() may help: http://stackoverflow.com/a/2550630
    # Save to file: http://docs.python.org/tutorial/inputoutput.html#reading-and-writing-files
    pass

def main():
    fb_feed = get_fb_feed()
    if not fb_feed:
        print "Location: fb_authentication.py\n"
        return

    print "Content-Type: text/html\n"
    print fb_feed

    if DEBUG:
        pretty_print_json(fb_feed)

    youtube_links = extract_youtube_links(fb_feed)
    print youtube_links

if __name__ == "__main__":
    main()


# Future TODO:
# Page through all the facebook results
# Setup OAuth?
# Setup CSS
