# -*- coding: utf-8 -*-

"""lyrico

Usage:
  lyrico [<source_dir>]
  lyrico (enable | disable) (<lyrico_action>)
  lyrico set (<dir_type>) (<full_path_to_dir>)
  lyrico (-h | --help)
  lyrico --version
  lyrico --settings

Options:
  -h --help     Show this screen.
  --version     Show version.
  --settings    Show current settings.
"""

from __future__ import print_function
from __future__ import unicode_literals

import platform

from .docopt import docopt

from .song import Song
from .song_helper import get_song_list
from .settings import Config

# testpypi 0.2.15
__version__ = "0.1.0"


def main():

	# Fix console for windows users
	if platform.system() == 'Windows':
		import win_unicode_console
		win_unicode_console.enable()

	args = docopt(__doc__, version = ('lyrico ' + __version__))

	# The check_config flag instructs the "Config.load_config" to skip the 'BadConfigError's.
	# So only when user is running downloads, the config must be valid.
	# When user is running cmds to update config, it will be always loaded
	# regardless of values of the settings.
	check_config = not(args['--settings'] or args['disable'] or args['enable'] or args['set'])

	Config.load_config(check_config)
	if not Config.is_loaded:
		# Config not loaded due to exceptions. Error logged by exception handlers.
		return

	# return
	
	if args['--settings']:
		# show current settings
		Config.show_settings()
		return

	if args['disable'] or args['enable'] or args['set']:
		# User is updating config

		if args['set']:
			# setting 'lyrics_dir' or 'source_dir'

			# This general try catch block is intended for os.makedirs call if
			# it raises OSError which is not due to directory already existing or
			# some other error than OSError
			try:
				Config.set_dir(args['<dir_type>'], args['<full_path_to_dir>'])
			except Exception as e:
				print(e)


		if args['enable'] or args['disable']:
			# setting 'save_to_file', 'save_to_tag' or 'overwrite'.

			# detect wether user wants to enable or disable a lyrico action
			update_type = 'enable' if args['enable'] else 'disable'
			Config.update_lyrico_actions(args['<lyrico_action>'], update_type)
	else:
		# User wants to download lyrics.

		if args['<source_dir>']:
			# if lyrico <source_dir> invocation is used:
			# update user's "source_dir" in config
			# update Config class' 'source_dir' class variable

			# This general try catch block is intended for os.makedirs call if
			# it raises OSError which is not due to directory already existing or
			# some other error than OSError
			try:
				set_dir_success = Config.set_dir('source_dir', args['<source_dir>'])
			except Exception as e:
				print(e)
				# Don't go ahead with excution since user gave bad path or might have
				# correct system settings?
				return

			# For this usage if user provides non existing dir, return by using boolean
			# return value of Config.set_dir
			if not set_dir_success:
				return

			# update class variable so that new setting is reflected across modules.
			Config.source_dir = args['<source_dir>']
				
		song_list = [Song(song_path) for song_path in get_song_list(Config.source_dir)]
		print(len(song_list), 'songs detected.')
		print('Metadata extracted for', (str(Song.valid_url_count) + '/' + str(len(song_list))), 'songs.')

		for song in song_list:
			if song.lyrics_wikia_url:
				song.download_lyrics()

			else:
				if song.title:
					print(song.title, 'was ignored.', song.error)
				else:
					print(song.path, 'was ignored.', song.error)

		print('\nBuilding log...')
		Song.log_results(song_list)
		print('FINISHED')
		
		# Disable windows unicode console anyways
		if platform.system() == 'Windows':
			win_unicode_console.disable()


