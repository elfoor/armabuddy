import aiohttp
import re
import logging
from wa_encoder import WA_Encoder

class WA_Gamelist():
	def __init__(self, **kwargs):

		if not 'gamelist_urls' in kwargs or not isinstance(kwargs['gamelist_urls'], list):
			raise ValueError('Invalid gamelist.')

		if not all(isinstance(url, str) for url in kwargs['gamelist_urls']):
			raise ValueError('Invalid gamelist URL list.')

		self.logger = logging.getLogger('WA_Logger')
		self.games = []
		self.regexp = re.compile(r'^<GAME\s(?P<title>.*?)[^\S\xA0](?P<user>.*?)\s(?P<host>.*?)\s(?P<country>.*?)\s(?P<unknown_1>.*?)\s(?P<private>.*?)\s(?P<gameid>.*?)\s(?P<unknown_2>.*?)><BR>$', re.MULTILINE)
		self.gamelist_urls = kwargs['gamelist_urls']
		self.session = aiohttp.ClientSession()
		self.headers = {
			'User-Agent': 'T17Client/3.8 (Steam)',
			'UserLevel': '0',
			'UserServerIdent': '2'
		}

	async def fetch(self):
		games = []
		for list in self.gamelist_urls:
			self.logger.warning(f' * Fetching gamelist: {list}.')
			response = await self.session.get(list, headers = self.headers)
			data = await response.read()
			html = WA_Encoder.decode(data)
			for game in self.regexp.finditer(html):
				game = game.groupdict()
				games.append(game)

		self.logger.warning(f' * Aggregated gamelists and found {len(games)} active games.')
		self.games = games
		return games