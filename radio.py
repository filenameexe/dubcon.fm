#!/usr/bin/env python

# Import Python Classes
import cgi
import os
import shelve
import sys
import time
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
DEBUG = False

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

def merge_fb_feed(feed_id, first_created_time, fb_feed):
    '''Get the Facebook feed using a facebook access token and feed id.'''

    radio_feed_url = '{0}{1}/feed?access_token={2}&format=json&limit=25'.format(
                            graph_url,
                            feed_id,
                            form.getvalue('access_token'))

    if DEBUG or True:
        print 'Curl URL:',radio_feed_url

    # Run through all the posts in the feed until all posts have been returned
    stop_paging = False
    while True:
        # Grab the JSON'd response
        paged_data = curl_to_json(radio_feed_url)

        # If the response was blank, return Nothing
        # Typically due to authentication failure
        if not paged_data:
            return

        # Cycle through this request's posts
        for post in paged_data['data']:
            # Ensure that each post is newer than the last recorded post
            if first_created_time >= int(time.mktime(time.strptime(post['created_time'], '%Y-%m-%dT%H:%M:%S+0000'))):

                # Break when this post is the same or earlier timestamp than the last known post
                stop_paging = True
                break

            # Add this post to the known list of posts
            fb_feed['data'].append(post)

        # Stop posting requests if there is nothing else to be paged
        if 'paging' not in paged_data or stop_paging:
            break

        # Assign the next page request for the next iteration of this loop
        radio_feed_url = paged_data['paging']['next']

    # Return our modified fb_feed
    # Note: Even though the dictionary has already been modified and doesn't need to be returned
    # The earlier return statement is to catch authentication errors
    return fb_feed

def extract_youtube_links(fb_feed):
    '''Get all youtube links from the returned fb feed.'''

    first_created_time = False

    # Create an empty list
    youtube_links = []

    # Loop through the fb_feed's data section. Call each item 'post'.
    for post in fb_feed['data']:
        if not first_created_time:
            first_created_time = int(time.mktime(time.strptime(post['created_time'], '%Y-%m-%dT%H:%M:%S+0000')))

        # Inspect each post
        # print pretty_print_json(post) # <-- this is currently commented out

        # Check if the key 'link' exists in this post and that
        # The substring 'youtube.com' exists in post['link']
        if 'link' in post and 'youtube.com' in post['link']:
            # If so, add this to the list
            youtube_links.append(post['link'])

    # Return this list
    return first_created_time, youtube_links

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

def retrieve_saved_feed(feed_id):
    '''Get the saved feed from a previous connection'''

    # Initialize the variables in case there was no previous session
    first_created_time = 0
    fb_feed = {'data': []}

    # Try to read the saved session from the database
    radio_db = shelve.open('radio.db')
    try:
        first_created_time = radio_db[feed_id]['first_created_time']
        fb_feed = radio_db[feed_id]['fb_feed']
    except KeyError:
        pass
    finally:
        radio_db.close()

    return first_created_time, fb_feed

def save_feed(feed_id, first_created_time, fb_feed):
    '''Save this session for future use and caching'''

    # Open database
    radio_db = shelve.open('radio.db')
    try:
        # Create new array to save
        to_save = {}
        to_save['first_created_time'] = first_created_time
        to_save['fb_feed'] = fb_feed

        # Save new array under feed_id
        radio_db[feed_id] = to_save
    finally:
        radio_db.close()


def main():
    '''Main method'''

    # Read and convert the feed_id to a string
    global feed_id
    feed_id = str(feed_id)

    # Read from the cached database
    first_created_time, fb_feed = retrieve_saved_feed(feed_id)

    # Read the newest posts
    fb_feed = merge_fb_feed(feed_id, first_created_time, fb_feed)
    if not fb_feed:
        # Redirect for authentication if reads failed
        print "Location: fb_authentication.py\n"
        return

    # Enable CGI printing
    print "Content-Type: text/html\n"

    if DEBUG:
        pretty_print_json(fb_feed)

    # Extract the newest time and youtube links
    first_created_time, youtube_links = extract_youtube_links(fb_feed)

    # Save the current feed information to the cache database
    save_feed(feed_id, first_created_time, fb_feed)

    if DEBUG:
        print youtube_links

if __name__ == "__main__":
    main()


# Future TODO:
# DONE Page through all the facebook results
# DONE Setup OAuth?
# Setup CSS
# Choose stations
