import aiohttp
import asyncio
import re
import logging
# import traceback


class WA_Gamelist:
    def __init__(self, **kwargs):
        assert isinstance(kwargs.get('urls'), list), 'Invalid gamelist'
        assert all(isinstance(url, str) for url in kwargs['urls']), 'Invalid gamelist URL list.'
        assert isinstance(kwargs.get('interval'), int), 'Invalid interval.'

        self.logger = logging.getLogger('WA_Logger')
        self.interval = kwargs['interval']
        self.games = []
        self.regexp = re.compile(  # Fields are space separated, user provided spaces get converted to \xA0 (NBSP)
            r'^<GAME\x20'
            r'(?P<title>.*?)\x20'
            r'(?P<user>.*?)\x20'
            r'(?P<host>.*?)\x20'
            r'(?P<country>.*?)\x20'
            r'(?P<unknown_1>.*?)\x20'
            r'(?P<private>.*?)\x20'
            r'(?P<gameid>.*?)\x20'
            r'(?P<packed_flag_id>.*?)'
            r'><BR>$',
            re.MULTILINE
        )
        self.gamelist_urls = kwargs['urls']
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30))
        self.headers = {
            'User-Agent': 'T17Client/3.8.1 (Steam)',
            'UserLevel': '0',
            'UserServerIdent': '2'
        }

    async def fetch(self):
        games = []
        for url in self.gamelist_urls:
            self.logger.warning(f' * Fetching gamelist: {url}.')
            try:
                response = await self.session.get(url, headers=self.headers)
            except Exception as e:
                self.logger.warning(f' ! {e}')
                continue

            data = await response.read()
            html = data.decode('wa1252')
            for game in self.regexp.finditer(html):
                games.append(game.groupdict())

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
                # traceback.print_exception(type(e), e, e.__traceback__)
                fail += 1
                self.logger.warning(f' ! Fetching gamelist has failed {fail} times in a row.')
                self.logger.warning(f' ! {e}')
                # if fail >= 3:
                #     self.logger.warning(' ! Fetching gamelist has failed the maximum allowed times in a row.')
                #     raise
