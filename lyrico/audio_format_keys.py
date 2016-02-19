
"""
	This module simpley holds the keys used to extract data from
	mutagens tags objects for the supported audio formats
"""

from __future__ import print_function
from __future__ import unicode_literals


VORBIS_COMMENTS_KEYS = {
	'artist': 'artist',
	'title': 'title',
	'album':'album',
	'lyrics':'LYRICS'
}

MP4_KEYS = {
	'artist': '\xa9ART',
	'title': '\xa9nam',
	'album':'\xa9alb',
	'lyrics':'\xa9lyr'
}

WMA_KEYS = {
	'artist': 'Author',
	'title': 'Title',
	'album':'WM/AlbumTitle',
	'lyrics':'WM/Lyrics'
}



FORMAT_KEYS = {
	
	#ID3 TAGS
	'mp3': {
		'artist': 'TPE1',
		'title': 'TIT2',
		'album':'TALB',
		'lyrics':'USLT'
	},

	'mp4' : MP4_KEYS,
	'm4a' : MP4_KEYS,

	'flac': VORBIS_COMMENTS_KEYS,
	'OGG' : VORBIS_COMMENTS_KEYS,

	'WMA' : WMA_KEYS,
	'wma' : WMA_KEYS
}


