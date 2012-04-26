#!/usr/bin/env python

# Import Python Classes
import cgi
import os
import re
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

    # Using %s or .format() may help: http://stackoverflow.com/a/2550630
    # http://docs.python.org/tutorial/inputoutput.html

    # Remove this fake list after you understand what's going on
    youtube_ids = ['unKR9WupoSE', '33kaBjW5QwA', 'EZnf3BGnJoc']

    # This is the url that we will use later when embedding
    # Here are the full list of parameters:
    # https://developers.google.com/youtube/player_parameters#Parameters
    youtube_url = '''
        http://www.youtube.com/v/{0}?
            version=3
            &iv_load_policy=3
            &showsearch=0
            &autohide=1
            &autoplay=1
            &hd=1
            &modestbranding=1
            &playlist={1}
    '''

    # Make the {0}'s be the first element of youtube_ids
    # Make the {1}'s be the list from the first element to the last that are
    # joined together by ,'s
    youtube_url = youtube_url.format(
        youtube_ids[0],
        ','.join(youtube_ids[1:])
    )

    if DEBUG:
        print youtube_url

    # Replace all &'s with the correct html encoding
    youtube_url = re.sub('&', '&amp;', youtube_url)

    # Remove all spaces (since the spaces were only for nicer code)
    youtube_url = re.sub('\n', '', youtube_url)
    youtube_url = re.sub(' ', '', youtube_url)

    # Resolution map for how big videos should be to automatically play
    # at a set resolution
    # Only one mapping is currently used. The rest will follow.
    resolution_map = {
        1080: (1920, 1080 + 30),
        720: (1280, 720 + 30),
        480: (720, 480 + 30),
        360: (480, 360 + 30),
        240: (350, 240 - 40)
    }

    # The actual embedding that YouTube provides
    youtube_embedding = '''
        <div style="width: {1[0]}px; height: {1[1]}px; margin: 0 auto;">
            <object width="{1[0]}" height="{1[1]}">
                <param name="movie" value="{0}"></param>
                <param name="allowScriptAccess" value="always"></param>
                <embed type="application/x-shockwave-flash" allowscriptaccess="always"
                       width="{1[0]}" height="{1[1]}" src="{0}"></embed>
            </object>
        </div>
    '''

    # Hard code the resolution for now
    # Later we will let the user choose this
    resolution = 1080

    # Return the youtube embedding where {0}'s replaced by the youtube_url
    # and {1[0]} read the first number of the resolution map
    # and {1[1]} read the second number of the resolution map
    return youtube_embedding.format(youtube_url, resolution_map[resolution])


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

    # Extract all the youtube ids from the youtube links
    youtube_ids = extract_youtube_ids(youtube_links)

    # Print the embedded playlist to the html page
    print construct_youtube_embed(youtube_ids)

    # Save the current feed information to the cache database
    save_feed(feed_id, first_created_time, fb_feed)

    if DEBUG:
        print youtube_links

if __name__ == "__main__":
    main()


# Future TODO:
# DONE Page through all the facebook results
# DONE Setup OAuth?
# Extract the YouTube IDs
# Choose different stations
# Setup CSS
# Remove dead videos
