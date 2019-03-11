# -*- coding: utf-8 -*-


from __future__ import print_function
from __future__ import unicode_literals

import os
import glob2

import logging

logger = logging.getLogger(__name__)

try:
	# Import the base class for all configparser errors as BaseConfigParserError
	# >3.2
	from configparser import ConfigParser
	from configparser import Error as BaseConfigParserError
except ImportError:
	# python27
	# Refer to the older SafeConfigParser as ConfigParser
	from ConfigParser import SafeConfigParser as ConfigParser
	from ConfigParser import Error as BaseConfigParserError

from .helper import get_config_path
from .helper import BadConfigError

# Maintian a dict of lyrico actions to check target on update_lyrico_actions()
# Also save the corresponding section in 

LYRICO_ACTIONS = {
	'save_to_file': 'actions',
	'save_to_tag': 'actions',
	'overwrite': 'actions',

	'lyric_wikia': 'sources',
	'lyrics_n_music': 'sources',
	'musix_match': 'sources',
	'lyricsmode' : 'sources',
	'az_lyrics': 'sources',
}

# Used to print commandline logging for enable/disable sources 
SOURCE_STR_MAP = {
	'lyric_wikia' : 'Lyric Wikia',
	'lyrics_n_music': 'LYRICSnMUSIC',
	'musix_match': 'musiXmatch',
	'lyricsmode': 'LYRICSMODE',
	'az_lyrics': 'AZLyrics',
}

class Config():
	
	"""
		Class wrapper build around user settings loaded from
		config.ini

		All setting are stored are class variables and all methods are
		static methods. 

		A Config object is never instantiated, only the class is imported
		into other modules to access class variables and methods. 

	"""

	# Audio formats supported are not loaded from config.ini

	# This list is used by the 'glob2' module to scan 'source_dir' for audio files.
	audio_formats = ['mp3', 'flac', 'm4a', 'mp4', 'ogg', 'oga', 'wma']

	lyrics_dir = None
	source_dir = None

	save_to_file = True
	save_to_tag = False

	overwrite = False
	lyric_files_in_dir = None

	# Flag to test if the config has been loaded
	is_loaded = False

	@staticmethod
	def load_config(check_config):

		"""
			Called only once by main to read user settings from config.ini
			and save them to the class variables.

			Only raises BadConfigError when check_config is True.
		"""

		try:
			conf = ConfigParser()

			# get_config_path raises BadConfigError(0,'') if config.ini is not found.
			config_path = get_config_path()

			conf.read(config_path)

			# save references to conf, and config_path in class variables
			Config.config_path = config_path
			Config.conf = conf

			Config.source_dir = conf.get('paths', 'source_dir')
			Config.lyrics_dir = conf.get('paths', 'lyrics_dir')

			# This forces user to set dirs before running the app for first time.
			if (Config.lyrics_dir == 'None' or Config.source_dir == 'None') and check_config:
				# see which directory in not set and raise BadConfigError with that as value 
				value = 'source_dir' if Config.source_dir == 'None' else 'lyrics_dir'
				raise BadConfigError(1, value)

			Config.save_to_file = conf.getboolean('actions', 'save_to_file')
			Config.save_to_tag = conf.getboolean('actions', 'save_to_tag')

			# if user disable both saving mode. Notify & force user to correct on next run.
			if (not Config.save_to_file and not Config.save_to_tag) and check_config:
				raise BadConfigError(2, 'Bad Config')

			Config.overwrite = conf.getboolean('actions', 'overwrite')

			# Load all the sources
			Config.lyric_wikia = conf.getboolean('sources', 'lyric_wikia')
			Config.lyrics_n_music = conf.getboolean('sources', 'lyrics_n_music')
			Config.musix_match = conf.getboolean('sources', 'musix_match')
			Config.lyricsmode = conf.getboolean('sources', 'lyricsmode')
			Config.az_lyrics = conf.getboolean('sources', 'az_lyrics')

			# if user disables all sources. Notify & force user to enable one.
			if ((not Config.lyric_wikia and not Config.lyrics_n_music and 
				not Config.az_lyrics and not Config.musix_match and not Config.lyricsmode) and check_config):
				raise BadConfigError(3, 'Bad Config')

			# Loading this with user config, we need to call the load_config only once at start.
			Config.lyric_files_in_dir = glob2.glob(os.path.join(Config.lyrics_dir, '**/*.txt'))

			Config.is_loaded = True

		# Exception blocks just log errors. Program execution is stopped by using the
		# Config.is_loaded flag test.

		except BadConfigError as e:
			
			if e.errno == 0:
				logger.info('Unable to find config.')
				logger.info('Please try installing lyrico again or contact creator.')

			if e.errno == 1:
				logger.info(e.value, 'is not set. ', end="")
				logger.info('Please use the "set" command to set', (value + '.'))
				logger.info('use "lyrico --help" to view commands.')
				Config.show_settings()
			
			if e.errno == 2:
				logger.info('Both "save_to_file" and "save_to_tag" modes are disabled. Please enable one.')
				logger.info('use "lyrico --help" to view commands.')
				Config.show_settings()

			if e.errno == 3:
				logger.info('All lyrics sources are disabled. Please enable one.')
				logger.info('use "lyrico --help" to view commands.')
				Config.show_settings()

		# Catch all config parser errors
		except BaseConfigParserError as e:
			logger.info('Unable to load config.')
			logger.info(e)

		# Catch file handling errors
		except IOError as e:
			logger.info('Unable to load config.')
			logger.info(e)

	@staticmethod
	def set_dir(dir_type, path):

		"""
			Takes an absolute path as saves it as 'source_dir' or 'lyrics_dir'
			in config.ini.
			path is user input from the cmdline.
		"""

		if dir_type != 'source_dir' and dir_type != 'lyrics_dir':
			logger.info('Invalid "dir_type". Only "source_dir" or "lyrics_dir" are valid types.')
			logger.info('You gave "dir_type":', dir_type)
			logger.info('use "lyrico --help" to view commands.')
			return False

		# If user is setting "source_dir", return if the path provided does not exist.
		# This improves the usage - lyrico <source_dir>
		if dir_type == 'source_dir' and not os.path.isdir(path):
			logger.info('"source_dir" does not exist. ', end="")
			logger.info('You gave "source_dir":', path)
			logger.info('Please enter path to an existing folder.')
			return False

		# make directory if user is setting "lyrics_dir" and it does not exists.
		# Refer http://stackoverflow.com/a/14364249/2426469
		if dir_type == 'lyrics_dir':
			try:
				os.makedirs(path)
				logger.info('Directory does not exist. Creating new one.')
			except OSError:
				if not os.path.isdir(path):
					# this exception is handled by function calling set_dir
					raise
		
		saved = Config.save_config_to_file('paths', dir_type, path)
		
		# save_config_to_file returns False on catching excepions
		if not saved:
			# If updating config file fails for some reason, don't print success log.
			# Errors are logged by save_config_to_file.
			return False
		
		logger.info(dir_type, 'updated.')
		if dir_type == 'source_dir':
			logger.info('lyrico will scan the following folder for audio files:')
		else:
			logger.info('lyrico will save lyrics files in the following folder:')
		logger.info('    ', path)
		return True

	@staticmethod
	def update_lyrico_actions(target, update_type):

		if target not in LYRICO_ACTIONS:
			logger.info('Invalid lyrico action change attempted')
			logger.info('''"save_to_file", "save_to_tag" and "overwrite" are the only settings that can be enabled or disabled.''')
			logger.info('''"lyric_wikia", "lyrics_n_music", "musix_match", "lyricsmode" and "az_lyrics" are the only sources that can be enabled or disabled.''')
			logger.info('You attempted to change:', target)
			logger.info('use "lyrico --help" to view commands.')
			return 

		# User is updating valid action/source
		value = 'True' if update_type == 'enable' else 'False'
		log_str = '' if update_type == 'enable' else 'not '
		
		saved = Config.save_config_to_file(LYRICO_ACTIONS[target], target, value)
		# save_config_to_file returns False on catching excepions
		if not saved:
			# If updating config file fails for some reason, don't print success log.
			# Errors are logged by save_config_to_file.
			return

		logger.info(target, (update_type + 'd'))

		if target == 'save_to_file':
			logger.info('lyrico will %ssave the downloaded lyrics to text files.' % log_str)

		elif target == 'save_to_tag':
			logger.info('lyrico will %sembed the downloaded lyrics into song tags.' % log_str)

		elif target == 'overwrite':
			if update_type == 'disable':
				logger.info('lyrico will detect the songs that already have lyrics, and will ignore them.')
			else:
				logger.info('''lyrico will download lyrics for all songs detected in "source_dir" and overwrite lyrics if already present.''')
		else:
			# Action is to enable/disable a source.
			logger.info('lyrico will %suse %s as a source for lyrics.' % (log_str, SOURCE_STR_MAP[target]))

	@staticmethod
	def show_settings():
		
		logger.info('Your current settings:\n')
		# get list of section in config
		for section in Config.conf.sections():
			# for each section get list items.
			# items are returned as list of tuples of type (key, value)
			logger.info(section.upper())
			for item in Config.conf.items(section):
				logger.info('   ', item[0], '=', item[1])
			logger.info('\n')

	@staticmethod
	def save_config_to_file(section, key, value):
		try:
			Config.conf.set(section, key, value)
			with open(Config.config_path, 'w') as configfile:
				Config.conf.write(configfile)
			return True

		# Catch all config parser errors
		except BaseConfigParserError as e:
			logger.info('Unable to save settings to config.')
			logger.info(e)
			return False

		# Catch file handling errors
		except IOError as e:
			logger.info('Unable to save settings to config.')
			logger.info(e)
			return False