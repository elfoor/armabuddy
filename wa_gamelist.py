import aiohttp
import asyncio
import re
import logging
import traceback
from wa_encoder import WA_Encoder


class WA_Gamelist():
    def __init__(self, **kwargs):

        if not 'urls' in kwargs or not isinstance(kwargs['urls'], list):
            raise ValueError('Invalid gamelist.')

        if not all(isinstance(url, str) for url in kwargs['urls']):
            raise ValueError('Invalid gamelist URL list.')

        if not 'interval' in kwargs or not isinstance(kwargs['interval'], int):
            raise ValueError('Invalid interval.')

        self.logger = logging.getLogger('WA_Logger')
        self.interval = kwargs['interval']
        self.games = []
        self.regexp = re.compile(
            r'^<GAME\s'
            r'(?P<title>.*?)[^\S\xA0]'
            r'(?P<user>.*?)\s'
            r'(?P<host>.*?)\s'
            r'(?P<country>.*?)\s'
            r'(?P<unknown_1>.*?)\s'
            r'(?P<private>.*?)\s'
            r'(?P<gameid>.*?)\s'
            r'(?P<packed_flag_id>.*?)'
            r'><BR>$',
            re.MULTILINE
        )
        self.gamelist_urls = kwargs['urls']
        self.session = aiohttp.ClientSession()
        self.headers = {
            'User-Agent': 'T17Client/3.8.1 (Steam)',
            'UserLevel': '0',
            'UserServerIdent': '2'
        }

    async def fetch(self):
        games = []
        for list in self.gamelist_urls:
            self.logger.debug(f' * Fetching gamelist: {list}.')
            response = await self.session.get(list, headers=self.headers)
            data = await response.read()
            html = WA_Encoder.decode(data)
            for game in self.regexp.finditer(html):
                game = game.groupdict()
                games.append(game)

        self.logger.warning(f' * Aggregated gamelists and found {len(games)} active games.')
        self.games = games
        return games

    async def update(self, discord):
        fail = 0
        while True:
            try:
                await asyncio.sleep(self.interval)
                result = await self.fetch()
                embed = await discord.create_gamelist(result)
                await discord.update_gamelists(content=None, embed=embed)
                fail = 0
            except Exception as e:
                traceback.print_exception(type(e), e, e.__traceback__)
                fail += 1
                self.logger.warning(f' ! Fetching gamelist has failed {fail} times in a row.')
                self.logger.warning(' ! ' + str(e))
                if fail >= 3:
                    self.logger.warning(f' ! Fetching gamelist has failed the maximum allowed times in a row.')
                    raise
