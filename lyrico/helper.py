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

	# If string only empty spaces return None
	if not s or s.isspace():
		return None

	# remove any white-space from beginning or end of the string
	s = s.strip()

	# remove double white-spaces or tabs if any
	s = re.sub(r'\s+', ' ', s)

	return s