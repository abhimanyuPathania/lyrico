# -*- coding: utf-8 -*-


"""
	This module downloads lyrics using API LYRICSnMUSIC. LnM API allows 
	a single get request which takes in an api_key, title and artist to
	serch for lyrics. JSON response does not contain entire lyrics but a
	URL to their page which has the full lyrics (licensed).

	Module retrieves the URL and makes a second request from which it scraps off
	the lyrics.

"""

from __future__ import print_function
from __future__ import unicode_literals

import re
import json
import requests

from requests import ConnectionError, HTTPError, Timeout
from bs4 import BeautifulSoup

from .build_requests import get_lyrico_headers, get_lnm_api_key


base_lnm_url = 'http://api.lyricsnmusic.com/songs'

# Defining these outside donwload_from_lnm function makes
# random visitor per lyrico operation and not per each download in an operation
request_headers = get_lyrico_headers()
api_key = get_lnm_api_key()


def donwload_from_lnm(song):
	
	"""
		Takes reference to the song object as input and
		adds lyrics to self.lyrics or add error string to self.error
		property of the song object. 
	"""


	# temp var to hold value for final checking
	lyrics = None

	# Redundant value checking. This function cannot be called without either of
	# artist, title present. To be removed after testing.
	if not song.artist or not song.title:
		if not song.error:
			# Same as added by get_song_data
			song.error = 'Artist name or song title not found.'
		return

	
	# Build the initial JSON request data
	data = {
		'api_key': api_key,
		'artist': song.artist,
		'track': song.title
	}


	# Add additional content type header for the JSON request
	request_headers['Content-type'] = 'application/json'

	try:
		print('\tTrying LYRICSnMUSIC...')
		# On unable to find data, this request returns and empty list(JSON string)
		# but with 200 success code
		r_json = requests.get(base_lnm_url, params=data, headers = request_headers)
		# Raise HTTPError for bad requests
		r_json.raise_for_status()

		resp_json = json.loads(r_json.text)

		# empty list
		if not resp_json:			
			# Update error field of Lyrics namedtuple and return
			song.error = 'Lyrics not found. Check artist or title name and retry.'
			# return statement is required or the 'else' block runs
			return

		lyrics_url = resp_json[0].get('url')
		if not lyrics_url:
			song.error = 'Lyrics not found. Check artist or title name and retry.'
			return

		# remove the JSON content type header, since we are making the usual request
		del request_headers['Content-type']

		# make the second request for lyrics HTML page
		r_html = requests.get(lyrics_url, headers = request_headers)
		r_html.raise_for_status()

	# Catch network errors
	except (ConnectionError, Timeout):
		song.error = 'No network connectivity.'
	except HTTPError:
		song.error = 'Bad request. Lyrics not found. Check artist or title name.'
	
	# No exceptions raised and the HTML for lyrics page was fetched		
	else:
		soup = BeautifulSoup(r_html.text, 'html.parser')

		# LYRICSnMUSIC pages hold lyrics in a <pre> tag contained in <div> with id='main'
		main_div = soup.find(id="main")
		if main_div and main_div.pre:		
			lyrics = main_div.pre.get_text().strip()

			# remove the superflous '\r' characters. '\n' are already present.
			lyrics = re.sub(r'\r', '', lyrics)
		else:
			song.error = 'Lyrics not found. Check artist or title name and retry.'

	# Final checking. If lyrics not present, just assign the error string.
	# result.lyrics is still None
	if lyrics:
		song.lyrics = lyrics
		song.source = 'LnM'
	else:
		#don't overwrite any previous(connectivity) errors
		if not song.error:
			song.error = 'Lyrics not found. Check artist or title name and retry.'