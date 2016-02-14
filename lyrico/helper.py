# -*- coding: utf-8 -*-

"""
	Contains general helper functions and Error classes.
"""

from __future__ import print_function
from __future__ import unicode_literals

import sys
import re
import os


class BadConfigError(Exception):
	def __init__(self, errno, value):
		self.value = value
		self.errno = errno
	
	def __str__(self):
		return repr(self.value)


def get_config_path():
	
	"""
		Gets the absolute path of dir containing script running the function.
		Uses that to get the path of config file, since it is located in same dir.
		Checks if file exists and raises BadConfigError if missings.
	"""
	config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.ini')
	if os.path.isfile(config_path):
		return config_path
	else:
		raise BadConfigError(0, 'Bad Config')

def sanitize_data(s):
	"""Removes excess white-space from strings"""

	if not s:
		return None

	# If string only empty spaces return None
	if s.isspace():
		return None

	# remove any white-space from beginning or end of the string
	s = s.strip()

	# remove double white-spaces or tabs if any
	s = re.sub(r'\s+', ' ', s)

	return s

def get_wikia_url(artist, title):
	
	try:
		from urllib.parse  import quote
	except ImportError:
		# Python27
		from urllib import quote

	# replace spaces with underscores. This prints nicer URLs in log.
	# (wikia's URL router converts spaces to underscores)
	artist = artist.replace(' ', '_')
	title = title.replace(' ', '_')

	# For calling 'quote' in Python27, artist and title unicode objects
	# must be encoded. Choosing 'utf-8', since used by wikia and most browsers to encode URLs.
	if sys.version_info[0] < 3:
		artist = artist.encode('utf-8')
		title = title.encode('utf-8')

	# Call quote to encode other characters.
	lyrics_wikia_url = 'http://lyrics.wikia.com/wiki/%s:%s' % (quote(artist), quote(title))

	return lyrics_wikia_url