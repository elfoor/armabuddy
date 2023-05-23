from aiohttp import web
from urllib import parse
import logging


class WA_HTTP_Redir:
    VALID_QUERY_KEYS = ('Host', 'Port', 'Scheme', 'ID')

    def __init__(self, *args, **kwargs):
        self.loop = kwargs.get('loop')
        self.host_ip = kwargs.get('host_ip')
        self.host_port = kwargs.get('host_port')
        self.server_headers = kwargs.get('server_headers')
        self.logger = logging.getLogger('WA_Logger')
        self.runner = web.ServerRunner(web.Server(self.handler))

    def validate_request(self, request):
        if not request.query:
            return False
        if not all(key in self.VALID_QUERY_KEYS for key in request.query.keys()):
            return False
        try:
            if port := request.query.get('Port'):
                int(port)
        except ValueError:
            return False

        return True

    async def handler(self, request):
        queries = dict(request.query)
        headers = {k: v for k, v in request.headers.items() if k != 'Host'}

        if not self.validate_request(request):
            self.logger.warning(f' ! Got bad redirect request from {request.remote}.'
                                f" URL='{request.rel_url}' {headers=}")
            return

        redirect_host = queries.pop('Host')
        port = queries.pop('Port', None)

        self.logger.warning(f' * Serving redirect request from {request.remote}.'
                            f" Host='{redirect_host}' {port=} {queries=} {headers=}")
        raise web.HTTPMovedPermanently(
            headers=self.server_headers,
            location=''.join((
                f'wa://{redirect_host}',
                f':{port}' if port is not None else '',
                f'/?{parse.urlencode(queries)}'
            )))

    async def main(self):
        self.logger.warning(' * Starting HTTP redirector.')
        await self.runner.setup()
        site = web.TCPSite(self.runner, self.host_ip, self.host_port)
        await site.start()
        self.logger.warning(f' * HTTP redirector successfully started on {self.host_ip}:{self.host_port}.')
