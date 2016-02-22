
import copy
import random


user_agents = [
	'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:44.0) Gecko/20100101 Firefox/44.0',
	'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.109 Safari/537.36 OPR/35.0.2066.68',
	'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.109 Safari/537.36',
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
	'957db35ac62f27b3312c5f6d8e81c7'
]

# randint inculdes both upper and lower bounds

def get_lyrico_headers(site_name=None):
	
	# Since each module requesting from different souce uses the same
	# request headers for a lyrico operation, make deep copies of base headers
	# before giving it to modules.

	headers_copy = copy.deepcopy(request_headers)
	headers_copy['User-Agent'] = user_agents[random.randint(0,2)]
	return headers_copy

def get_lnm_api_key():
	return lnm_api_keys[random.randint( 0, (len(lnm_api_keys) - 1))]

def test_req_dic():
	print(request_headers)

