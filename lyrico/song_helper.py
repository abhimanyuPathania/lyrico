# -*- coding: utf-8 -*-

"""
	Contains helper functions specific to instantiate Song class.
"""

from __future__ import print_function


import os
import glob2
import urllib

from mutagen.easyid3 import ID3
from mutagen.mp4 import MP4
from mutagen.flac import FLAC

from .settings import Config
from .helper import sanitize_data



def get_key(tag, key, format):
	data = None
	result = None
	flac_lyrics_keys = ['UNSYNCED LYRICS', 'LYRICS', 'SYNCED LYRICS']

	if format == 'mp3':
		## get for mp3 tags is not fetching lyrics(None). Using getall instead.
		data = tag.getall(key)
		if not len(data):
			return result

		# for USLT(lyrics frame) only return lyrics if exist
		if key == 'USLT':
			result = data[0].text if len(data[0].text) else None
		else:
			# for TPE1, TIT2, TALB frames, the text field is a list itself
			# so we look one list deeper
			result = data[0].text[0]

	if format == 'm4a' or format == 'mp4' or format == 'flac':
		
		if format == 'flac' and key == 'UNSYNCED LYRICS':

			# for flacs loop through different keys to look for lyrics
			# UNSYNCED LYRICS will be used as standard for 'lyrico' 
			for flac_key in flac_lyrics_keys:
				# also try lowercases
				data = tag.get(key) or tag.get(key.lower())

				# if we find lyrics, stop looping
				if data:
					break
		else:
			# simple dictionary lookup
			data = tag.get(key)

		# mp4, flac tags(here simple dict) return None for keys that are not present
		if not data:
			return result

		result = data[0]

	return result


def get_song_data(path):
	
	""" 
		Extracts song artist, album, title and lyrics if present 
		from audio file.

		This is method is called by constructor of Song class which uses
		the dict returned to instantiate song objects.

		'path' is the absolute path to the audio file.  
	"""

	data = {}

	tag = None
	song_format = None
	
	lyrics_wikia_url = None
	lyrics_file_name = None
	lyrics_file_path = None

	lyrics_file_present = False
	lyrics_tag_present = False

	error = None

	# format will the part of string after last '.' character
	song_format = path[ path.rfind('.') + 1 : ]

	try:
		# Extract artist and title
		if song_format == 'mp3':
			tag = ID3(path)
			artist = get_key(tag, 'TPE1', song_format)
			title = get_key(tag, 'TIT2', song_format)
			album = get_key(tag, 'TALB', song_format)
			lyrics = get_key(tag, 'USLT', song_format)

		if song_format == 'flac':
			tag = FLAC(path)
			artist = get_key(tag, 'artist', song_format)
			title = get_key(tag, 'title', song_format)
			album = get_key(tag, 'album', song_format)
			lyrics = get_key(tag, 'UNSYNCED LYRICS', song_format)

		# used for m4a, mp4 containers and any aac, mp4 codecs
		if song_format == 'm4a' or song_format == 'mp4':
			tag = MP4(path)
			artist = get_key(tag, '\xa9ART', song_format)
			title = get_key(tag, '\xa9nam', song_format)
			album = get_key(tag, '\xa9alb', song_format)
			lyrics = get_key(tag, '\xa9lyr', song_format)

		# remove uncessary white-space
		artist = sanitize_data(artist)
		title = sanitize_data(title)
		album = sanitize_data(album)
		lyrics = sanitize_data(lyrics)

	except Exception as e:
		print(e)

	# build wikia URL, filename and filepath
	if artist and title:
		# replace spaces with underscores and call urllib.quote_plus to encode other characters
		lyrics_wikia_url = 'http://lyrics.wikia.com/wiki/%s:%s' % \
		( urllib.quote_plus(artist.replace(' ', '_')), urllib.quote_plus(title.replace(' ', '_')))

		
		lyrics_file_name = '%s - %s.txt' % (artist, title)
		lyrics_file_path = os.path.join(Config.lyrics_dir, lyrics_file_name)
	else:
		error = 'Artist name or song title not found.'


	# check if lyrics file already exists in LYRICS_DIR
	if lyrics_file_path in Config.lyric_files_in_dir:
		lyrics_file_present = True

	# check if lyrics already embedded in tag
	if lyrics:
		lyrics_tag_present = True

	# build dict
	data['tag'] = tag
	data['artist'] = artist
	data['title'] = title
	data['album'] = album
	data['format'] = song_format

	data['lyrics_wikia_url'] = lyrics_wikia_url
	data['lyrics_file_name'] = lyrics_file_name
	data['lyrics_file_path'] = lyrics_file_path

	data['lyrics_file_present'] = lyrics_file_present
	data['lyrics_tag_present'] = lyrics_tag_present

	data['error'] = error

	return data

def get_song_list(path):

	""" Return list of paths to all valid audio files in dir located at path.
		Valid audio formats are imported from settings module.
		Also checks for any inner directories."""

	song_list = []

	for ext in Config.audio_formats:
		pattern = '**\\*.' + ext
		song_list.extend(glob2.glob(os.path.join(path, pattern)))

	return song_list