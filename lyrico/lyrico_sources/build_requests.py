
from __future__ import print_function
from __future__ import unicode_literals

import copy
import random

import logging

logger = logging.getLogger(__name__)

user_agents = [
	'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:44.0) Gecko/20100101 Firefox/44.0',
	'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.109 Safari/537.36 OPR/35.0.2066.68',
	'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.109 Safari/537.36',
	'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.1 Safari/537.36',
	'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36',
	'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; AS; rv:11.0) like Gecko',
	'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)',
	'Mozilla/5.0 (Windows; U; MSIE 9.0; WIndows NT 9.0; en-US))',
]

request_headers = {
	'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
	'Accept-Encoding': 'gzip, deflate',
	'Accept-Language': 'en-GB,en-US;q=0.8,en;q=0.6',
	'DNT': '1',	
}

lnm_api_keys = [
	'5442d9796271ea7baf837dfb2bfb4c',
	'ccae79268ebd14d14df857b203e029',
	'5f7f6670358b899f4b6c69f61bd80c',
	'1ddd0fc509738936c81f61451bad1b',
	'867d86fe3d85f2dfea8a23a790863d',
	'a096049a914d27dc189f26b6d3777d',
	'881954ca4ae494d6f2030166158405',
	'fbeb6447d7b6e00dad7f1d98c305dc',
	'62bdc7f79844d6784cbf95cfa8ac6d',
	'957db35ac62f27b3312c5f6d8e81c7',
	'42969bb4db5edc7559819e7d8ff79c',
	'4eebd7b17388e32801dbd4a9136f05',
	'4d9ced669ed8d4f12b89857a9b047f',
	'eea4287ca87fb410fd2bff2d29f79c',
	'9be4b31867583ddc6daaf56dd83849',
	'2b8a4dbaa9b0d95652e33c1d1b32b6',
	'54abc1914ec3ef13d47b2ab522a9dd',
	'2d4c33d93333756dc18a1ab8ea6350',
	'911f4bd4c332a6462865888836615a',
	'7da59aae94b735702e9aba32d50b00',
	'f7b366b1270cca982ea06c6a316d58',
	'13a0fd2d15321938ade087088c9ba8'
]

# randint inculdes both upper and lower bounds

def get_lyrico_headers(site_name=None):
	
	# Since each module requesting from different souce uses the same
	# request headers for a lyrico operation, make deep copies of base headers
	# before giving it to modules.

	headers_copy = copy.deepcopy(request_headers)
	headers_copy['User-Agent'] = user_agents[random.randint(0, (len(user_agents) - 1))]
	return headers_copy

def get_lnm_api_key():
	return lnm_api_keys[random.randint( 0, (len(lnm_api_keys) - 1))]

def test_req_dic():
	logger.info(request_headers)
