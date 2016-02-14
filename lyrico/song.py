# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import unicode_literals


try:
    # For Python 3.0 and later
    from urllib.request import urlopen
    from urllib.error import HTTPError, URLError

except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import urlopen
    from urllib2 import HTTPError, URLError

import sys
import os
import socket
import codecs

from time import strftime
from mutagen.id3 import USLT
from bs4 import BeautifulSoup

from .song_helper import get_song_data, get_song_list
from .settings import Config

# If we are using python27, import codec module and replace native 'open'
# with 'codec.open' to write unicode strings to file.

if sys.version_info[0] < 3:
    import codecs
    open = codecs.open



class Song():
	"""Container objects repersenting each globbed song in DIR"""

	# holds count for songs for valid metadata
	valid_url_count = 0

	# Count for songs whose lyrics are successfully saved to file.
	lyrics_saved_to_file_count = 0

	# Count for songs whose lyrics are successfully saved to tag.
	lyrics_saved_to_tag_count = 0

	def __init__(self, path):

		self.path = path

		# extract data from song
		data = get_song_data(path)

		# Initialize instance variables from data extracted
		self.tag = data['tag']
		self.artist = data['artist']
		self.title = data['title']
		self.album = data['album']
		self.format = data['format']

		self.lyrics_wikia_url = data['lyrics_wikia_url']
		self.lyrics_file_name = data['lyrics_file_name']
		self.lyrics_file_path = data['lyrics_file_path']

		# If the required lyrics file is already present in LYRICS_DIR
		self.lyrics_file_present = data['lyrics_file_present']

		# If the required lyrics is already embedded in tag
		self.lyrics_tag_present = data['lyrics_tag_present']


		# Holds the downloaded lyrics
		self.lyrics = None

		# Final status to build log
		self.saved_to_tag = False
		self.saved_to_file = False

		self.error = data['error']

		# As the songs are read from the files, update the class variable.
		# This is count of songs that have valid artist and title.
		if self.lyrics_wikia_url:
			Song.valid_url_count += 1

	def download_lyrics(self):
		"""
		Makes HTTP request to self.lyrics_wikia_url.
		Stips HTML and extracts and sanitizes lyrics.
		Calls self.save_lyrics to save them.

		"""

		if not self.download_required():
			print('\nSkipping', self.artist, '-', self.title)
			print('Lyrics already present.')
			return

		try:
			# print('\nDownloading lyrics for:', self.artist, '-', self.title)
			print('URL -', self.lyrics_wikia_url)

			response = urlopen(self.lyrics_wikia_url)
			html = response.read()
			soup = BeautifulSoup(html, 'html.parser')

			lyricbox = soup.find(class_='lyricbox')

			if lyricbox:

				# remove script and div tags from the lyricbox(div)
				junk = lyricbox.find_all(['script', 'div'])
				for html_tag in junk:
					html_tag.decompose()

				# replace '<\br>' tags with newline characters
				br_tags = lyricbox.find_all('br')

				# loop over all <\br> tags and replace with newline characters
				for html_tag in br_tags:
					html_tag.replace_with('\n')

				# lyrics are returned as unicode object
				self.lyrics = lyricbox.get_text().strip()
			else:
				# lyricbox div absent if lyrics are not found
				self.error = 'Lyrics not found. Check artist or title name.'

		# Catch bad server response
		except HTTPError as e:
			## currently the bad requests return status code 404 and not html page without lyrics
			self.error = e.reason + '. Check title or artist name.' + ' Error code:' + str(e.code) 

		# catch all network errors
		except URLError as e:
			self.error = 'No network connectivity.'

		# catch socket error. Can get because of bot sniffing or bad connectivity.
		except socket.error as e:
			if e.errno == 10054:
				self.error = 'Socket Error 10054. Check network connectivity?'
			else:
				print(e)

		self.save_lyrics()

	def save_lyrics(self):
		"""
		Called by self.download_lyrics to save lyrics according to
		Config.save_to_file, Config.save_to_tag settings

		"""

		if self.lyrics and Config.save_to_file:
			try:
				with open(self.lyrics_file_path, 'w', encoding='utf-8') as f:
					f.write('Artist - ' + self.artist + '\n')
					f.write('Title - ' + self.title + '\n')

					album_str = 'Album - Unkown'
					if self.album:
						album_str = 'Album - ' + self.album			
					f.write(album_str)
					f.write('\n\n')

					f.write(self.lyrics)

				# update class variable
				Song.lyrics_saved_to_file_count += 1

				# update the Song instance flag
				self.saved_to_file = True

				print('Success: Lyrics saved to file.')

			except IOError as e:
				err_str = str(e)
				if e.errno == 22:
					err_str = 'Cannot save lyrics to file. Unable to create file with song metadata.'
				if e.errno == 13:
					err_str = 'Cannot save lyrics to file. The file is opened or in use.'
				if e.errno == 2:
					err_str = '"lyrics_dir" does not exist. Please set a "lyric_dir" which exists.'

				self.error = err_str
				print('Failed:', err_str)

		if self.lyrics and Config.save_to_tag:
			try:
				if self.format == 'mp3':
					# encoding = 3 for UTF-8
					self.tag.add(USLT(encoding=3, lang=u'eng', desc=u'lyrics.wikia',
									text=self.lyrics))

				if self.format == 'm4a' or self.format == 'mp4':
					self.tag['\xa9lyr'] = self.lyrics

				if self.format == 'flac':
					self.tag['UNSYNCED LYRICS'] = self.lyrics

				self.tag.save()
				self.saved_to_tag = True
				Song.lyrics_saved_to_tag_count += 1

				print('Success: Lyrics saved to tag.')

			except IOError as e:
				err_str = 'Cannot save lyrics to tag. The file is opened or in use.'
				self.error = err_str
				print('Failed:', err_str)

		if not self.lyrics:
			print('Failed:', self.error)

	def download_required(self):
		"""
		Checks if a lyrics are required to be download.
		Uses Config.save_to_file, Config.save_to_tag and Config.overwrite settings
		and returns True when download is required.

		"""
		if Config.overwrite:
			# If user wants to overwite existing lyrics, always download
			# and save according to Config.save_to_file, Config.save_to_tag settings
			return True
		else:

			# Do we need to download lyrics and save to file
			file_required = False

			# Do we need to download lyrics and save to tag
			tag_required = False

			if Config.save_to_file and not self.lyrics_file_present:
				# if user wants to save to file and the file is not
				# present in the set LYRICS_DIR, the we need
				# to download it and save to the file.
				file_required = True

			if Config.save_to_tag and not self.lyrics_tag_present:
				# if user wants to save to tag and the tag does not
				# has lyrics field saved, then we need
				# to download it and save to the tag.
				tag_required = True

			# If either is required, we need to make the download request.
			# Data is then saved accordingly to the settings.
			return file_required or tag_required

	def get_log_string(self):
		"""
		returns the log string of the song which is used in final log.

		"""
		template = '. \t{file}\t{tag}\t\t{song}\t\t{error}\n'
		log = {}

		# file_status and tag each have 4 possible values
			# 'Saved' - File or tag was saved successfully
			# 'Failed' - Download or save failed. Show error.
			# 'Ignored' - Ignored according to Config.save_to_file, Config.save_to_tag setting by user.
			# 'Present' - Detected tag or file and skipped download skipped by lyrico as per Config.overwrite setting.

		if Config.save_to_file:
			if not self.download_required():
				file_status = 'Present'
			else:
				if self.saved_to_file:
					file_status = 'Saved'
				else:
					file_status = 'Failed'
		else:
			file_status = 'Ignored'

		if Config.save_to_tag:
			if not self.download_required():
				tag = 'Present'
			else:
				if self.saved_to_tag:
					tag = 'Saved'
				else:
					tag = 'Failed'
		else:
			tag = 'Ignored'

		log['song'] = self.artist + ' - ' + self.title
		log['error'] = self.error

		log['file'] = file_status
		log['tag'] = tag

		return template.format(**log)

	@staticmethod
	def log_results(song_list):

		try:
			with open(os.path.join(Config.lyrics_dir, 'log.txt'), 'w', encoding='utf-8') as f:
				log_date = strftime("%H:%M:%S  %d-%m-%y")

				f.write('Log Date ' + log_date + '\n')
				f.write('\n')

				f.write('Audio files detected: ' + str(len(song_list)))
				f.write('\n')

				f.write('Metadata extracted for: ' + str(Song.valid_url_count))
				f.write('\n')

				f.write('Lyrics files saved: ' + str(Song.lyrics_saved_to_file_count))
				f.write('\n')

				f.write('Tags saved: ' + str(Song.lyrics_saved_to_tag_count))
				f.write('\n\n')

				table_header = '  \t[FILE]\t[TAG]\t\t\t[ARTIST-TITLE]\t\t\t\t[ERROR]\n'
				table_border = '='*100 + '\n'

				f.write(table_header)
				f.write(table_border)

				index_number = 1
				for song in song_list:
					f.write(str(index_number))
					f.write(song.get_log_string())
					index_number += 1
		except IOError as e:
			print('Unable to build log.')
			print('"lyrics_dir" does not exist. Please set "lyric_dir" to a folder which exists.')


