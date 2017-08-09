# -*- coding: utf-8 -*-

"""
	This module downloads lyrics from ChartLyrics.
        Documentation: http://www.chartlyrics.com/api.aspx

        We use the HTTP GET interface. First we search the lyrics using
        SearchLyrics and look for the right song in the returned XML.
	If there is a match we call GetLyrics and extracts lyrics from the XML
	response.

	Note we can't use SearchLyricsDirect, as the correct song is always the
	first result.
	
	URL structure: http://api.chartlyrics.com/apiv1.asmx/SearchLyricDirect?artist=string&song=string
"""

from __future__ import print_function
from __future__ import unicode_literals

import re
import json
import requests

from requests import ConnectionError, HTTPError, Timeout
import xml.etree.ElementTree as ElementTree

from .build_requests import get_lyrico_headers
from .lyrics_helper import test_lyrics


chartlyrics_SearchLyric_url = ' http://api.chartlyrics.com/apiv1.asmx/SearchLyric'
chartlyrics_GetLyric_url = ' http://api.chartlyrics.com/apiv1.asmx/GetLyric'

# Defining these outside donwload_from_chartlyrics function makes
# random visitor per lyrico operation and not per each download in an operation
request_headers = get_lyrico_headers()


def download_from_chartlyrics(song):

	"""
		Takes reference to the song object as input and
		adds lyrics to self.lyrics or add error string to self.error
		property of the song object. 
	"""


	# temp var to hold value for final checking
	lyrics = None


	resGetLyric = None
	namespaces =  { 'tns': 'http://api.chartlyrics.com/' }
	try:
		print('\tTrying ChartLyrics...')
		data = {
			'artist': song.artist,
			'song': song.title
		}
		resSearchLyric = requests.get(chartlyrics_SearchLyric_url, params=data, headers = request_headers)
		# Raise HTTPError for bad requests
		resSearchLyric.raise_for_status()

		root = ElementTree.fromstring(resSearchLyric.text.encode('utf-8'))
		for searchLyricResult in root.findall('tns:SearchLyricResult', namespaces):
			if (len(searchLyricResult) == 0):
				continue
			lyricArtist = searchLyricResult.find('tns:Artist', namespaces)
			lyricSong = searchLyricResult.find('tns:Song', namespaces)
			lyricId = searchLyricResult.find('tns:LyricId', namespaces)
			lyricChecksum = searchLyricResult.find('tns:LyricChecksum', namespaces)
			if (lyricArtist.text == song.artist
		  	and lyricSong.text == song.title
		  	and int(lyricId.text) > 0):
				data = {
					'lyricId': lyricId.text,
					'lyricChecksum': lyricChecksum.text
				}
				resGetLyric = requests.get(chartlyrics_GetLyric_url, params=data, headers = request_headers)
				# Raise HTTPError for bad requests
				resGetLyric.raise_for_status()
				break;


	# Catch network errors
	except (ConnectionError, Timeout):
		song.error = 'No network connectivity.'
	except HTTPError:
		song.error = 'Bad request. Lyrics not found. Check artist or title name.'
	
	# No exceptions raised and the HTML for lyrics page was fetched		
	else:
		if (resGetLyric):
			root = ElementTree.fromstring(resGetLyric.text.encode('utf-8'))
			lyricArtist = root.find('.//tns:LyricArtist', namespaces)
			lyricSong = root.find('.//tns:LyricSong', namespaces)
			lyricId = root.find('.//tns:LyricId', namespaces)
			lyric = root.find('.//tns:Lyric', namespaces)
			if (lyricArtist.text == song.artist
		  	and lyricSong.text == song.title
		  	and int(lyricId.text) > 0):
				lyrics = lyric.text

	if test_lyrics(lyrics):
		song.lyrics = lyrics
		song.source = 'chart'
		song.error = None
	else:
		#don't overwrite any previous(connectivity) errors
		if not song.error:
			song.error = 'Lyrics not found. Check artist or title name and retry.'
