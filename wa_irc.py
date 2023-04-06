import asyncio
import logging
import re
from datetime import datetime, timezone
from asyncirc.protocol import IrcProtocol
from asyncirc.server import Server
from irclib.parser import Message


class WA_IRC:
    def __init__(self, *args, **kwargs):
        assert kwargs, 'Missing required keyword arguments.'
        assert isinstance(kwargs.get('username'), str), 'Invalid username.'
        assert isinstance(kwargs.get('hostname'), str), 'Invalid WormNET server.'
        assert isinstance(kwargs.get('channels'), list), 'Invalid WormNET channel list.'
        assert isinstance(kwargs.get('port'), int), 'Invalid WormNET port.'
        assert isinstance(kwargs.get('loop'), asyncio.AbstractEventLoop), 'Invalid event loop.'

        self.logger = logging.getLogger('WA_Logger')
        self.wormnet = kwargs.pop('hostname')
        self.nickname = kwargs.pop('username')
        self.realname_parameters = '0 13 GB ArmaBuddy Discord Bot'  # FlagID, RankID, CountryCode, *Description
        self.channels = dict(zip(kwargs.get('channels'), [{} for _ in kwargs.get('channels')]))
        self.handlers = dict(zip(kwargs.get('channels'), [{} for _ in kwargs.get('channels')]))
        self.commands = dict(zip(kwargs.get('channels'), [False for _ in kwargs.get('channels')]))
        self.activity = dict(zip(kwargs.get('channels'), [{} for _ in kwargs.get('channels')]))
        self.activity_pm_replied = set()
        self.port = kwargs.pop('port')
        self.password = kwargs.pop('password', None)
        self.is_ssl = kwargs.pop('is_ssl', False)
        self.loop = kwargs.pop('loop')
        self.transcode = False
        self.reconnect_delay = 30
        self.server = Server(self.wormnet, self.port, self.is_ssl, password=self.password)
        self.reply_message = kwargs.get('reply_message', 'ArmaBuddy!')
        self.help_message = kwargs.get('help_message', '')
        self.ignore = kwargs.get('ignore', [])
        self.snooper = kwargs.get('snooper', 'WebSnoop')
        self.forward_message = lambda x: x

        # register handlers for every needed internal
        self.connection = IrcProtocol([self.server], self.nickname, realname=self.realname_parameters, loop=self.loop)
        self.connection.register_cap('userhost-in-names')
        self.connection.register('*', self.handle_command)
        self.connection.register('002', self.decide_transcode)  # Server name and version
        self.connection.register('376', self.join_channels)  # End of MOTD
        self.connection.register('JOIN', self.handle_entry)
        self.connection.register('PART', self.handle_entry)
        self.connection.register('QUIT', self.handle_entry)
        self.connection.register('352', self.handle_entry)  # WHO reply, lists client name, status, realname and more

        # horrible horrible hack for a horrible horrible library
        IrcProtocol.connection_lost = __class__.connection_lost

    async def connect(self):
        # begin connection
        self.logger.warning(' * Connecting to WormNET.')
        if await self.connection._connect(server=self.server):
            self.logger.warning(' * Connected to WormNET.')

        # wait for end of MOTD to signal proper connection
        if not await self.connection.wait_for('376', timeout=self.reconnect_delay):
            self.logger.warning(' ! Unable to connect to properly WormNET, attempting to reconnect.')
            return await self.connect()

        # wait until we lose connection
        while self.connection._connected:
            await asyncio.sleep(1)

        # if connection has died, attempt to restart it
        self.logger.warning(f' ! Disconnected from WormNET, attempting to reconnect in {self.reconnect_delay} seconds.')
        await asyncio.sleep(self.reconnect_delay)
        return await self.connect()

    async def decide_transcode(self, conn, message):
        # check if this is the community server, if so, disable transcoding of messages by monkey-patching IrcProtocol.data_received
        if len(message.parameters) >= 2 and 'ae.net.irc.server/WormNET' in message.parameters[1]:
            self.logger.warning(' * Disabled transcoding for WormNET messages.')
            IrcProtocol.data_received = __class__.transcode_off
            self.transcode = False
        else:
            self.logger.warning(' * Enabled transcoding for WormNET messages.')
            IrcProtocol.data_received = __class__.transcode_on
            self.transcode = True

    @staticmethod
    def transcode_off(self, data: bytes) -> None:
        self._buff += data
        while b'\r\n' in self._buff:
            raw_line, self._buff = self._buff.split(b'\r\n', 1)
            message = Message.parse(raw_line)
            for trigger, func in self.handlers.values():
                if trigger in (message.command, '*'):
                    self.loop.create_task(func(self, message))

    @staticmethod
    def transcode_on(self, data: bytes) -> None:
        self._buff += data
        while b'\r\n' in self._buff:
            raw_line, self._buff = self._buff.split(b'\r\n', 1)
            raw_line = raw_line.decode('wa1252')
            message = Message.parse(raw_line)
            for trigger, func in self.handlers.values():
                if trigger in (message.command, '*'):
                    self.loop.create_task(func(self, message))

    @staticmethod
    def connection_lost(self, exc) -> None:
        self._transport = None
        self._connected = False
        if self._quitting:
            self.quit_future.set_result(None)

    async def log(self, conn, message):
        self.logger.info(f' * IRC_RAW {message}')

    async def handle_entry(self, conn, message):
        # ignore messages triggered by self
        if message.prefix.nick == self.nickname:
            return

        channel = message.parameters[0][1:].lower()
        if message.command == 'JOIN':  # add user to channel set if joining
            if channel in self.channels:
                self.connection.send(f'WHO {message.prefix.nick}')
            if channel == 'help':
                self.loop.create_task(self.send_private(user=message.prefix.nick, message=self.help_message, delay=0.9))
                await asyncio.sleep(0)
        elif message.command == 'PART':  # remove user from channel set if parting
            if channel in self.channels:
                self.channels[channel].pop(message.prefix.nick, None)
        elif message.command == 'QUIT':  # remove user from all channel sets if quitting
            for channel in self.channels:
                self.channels[channel].pop(message.prefix.nick, None)
        elif message.command == '352':  # WHO request reponse
            channel = message.parameters[1][1:].lower()
            if channel in self.channels:
                user = message.parameters[5]
                realname_parameters = message.parameters[7][2:]
                self.channels[channel].update({user: realname_parameters})

    async def join_channels(self, conn, message):
        for channel_name in self.channels:
            # create new set containing user list
            self.logger.warning(f' * Joining WormNET channel: #{channel_name}!')

            self.connection.send(f'JOIN #{channel_name}')
            # give server a few seconds to give us NAMES, if none has been received after timeout propagate error
            result = await self.connection.wait_for('366', timeout=30)
            if result is None:
                raise Exception(f'Never received NAMES after joining WormNET channel #{channel_name}.')

            self.connection.send(f'WHO #{channel_name}')
            # give server a few seconds to give us user details, if none has been received after timeout propagate error
            result = await self.connection.wait_for('315', timeout=30)
            if result is None:
                raise Exception(f'Never received all user details from WHO request after joining WormNET channel'
                                f' #{channel_name}.')

            self.logger.warning(f' * Successfully joined WormNET channel: #{channel_name}!')

    async def clear_pm_activity(self, user, delay=0.0):
        if delay:
            await asyncio.sleep(delay)
        self.activity_pm_replied.discard(user)

    async def send_message(self, guild, origin, channel, message):
        # strip everything after \n to avoid sneaky user sending multiple commands in single string
        message = message.split('\n')[0]

        # prevent bot from letting itself get banned from n word, hex to avoid any potential github issues
        message = re.sub('\x6e\x69\x67\x67\x65\x72', '\x6e\x69\x67\x67\x65г', message, flags=re.IGNORECASE)

        message = f'PRIVMSG #{channel} :{message}'

        # keep message under 250 characters at least, in reality max length is 512
        message = (message[:250] + '[...]') if len(message) > 250 else message
        self.logger.warning(f' * Forwarding message from #{origin} on "{guild}" to WormNET #{channel}: {message}')
        await self.transport_write(message)

    async def send_private(self, user, message, delay=0.0):
        if delay:
            await asyncio.sleep(delay)

        # strip everything after \n to avoid sneaky user sending multiple commands in single string
        message = message.split('\n')[0]
        message = f'PRIVMSG {user} :{message}'

        self.logger.warning(f' * Forwarding PM to WormNET user {user}: {message}')
        await self.transport_write(message)

    async def transport_write(self, message):
        if self.connection._connected:
            message += '\r\n'
            message = message.encode('wa1252') if self.transcode else message.encode()
            self.connection._transport.write(message)
        else:
            self.logger.warning(' ! Could not forward message due to connection to IRC being down!')

    async def handle_command(self, connection, message):
        if message.command == '432':
            raise Exception(f'IRC error: Requested nickname contains invalid characters')
        if message.command == '433':
            raise Exception(f'IRC error: Requested nickname is already in use')
        if message.command == '474':
            raise Exception(f'IRC error: Banned from channel {message.parameters[1]}')
        if message.command == 'ERROR':
            raise Exception(f'IRC error: "{message.parameters}"')
        if message.command == 'PING':  # Seemingly a bug in AsyncIRC, shows only rarely but does show up.
            self.logger.warning(' ! Ping command not handled by AsyncIRC, skipping.')
            return

        # ignore commands triggered by self
        if message.prefix.nick == self.nickname:
            return

        # no channel when quitting, check for activity in help then post quit message and reason if so to help
        if message.command == 'QUIT':
            if message.prefix.nick in self.activity['help']:
                return await self.handlers['help'][message.command](connection, message)
            return  # don't process QUIT any further regardless

        if not message.parameters[0]:
            return  # nothing more to do if there isn't parameters

        if message.parameters[0][0] != '#' and message.command == 'PRIVMSG':
            # reply to all PM with predefined phrase, unless already replied within the limit
            if message.prefix.nick in self.activity_pm_replied:
                return self.logger.warning(f' * Ignoring PM within time limit on WormNET from {message.prefix.nick}:'
                                           f' {message.parameters[1]}')

            self.logger.warning(f' * Received PM on WormNET from {message.prefix.nick}: {message.parameters[1]}')
            self.activity_pm_replied.add(message.prefix.nick)
            self.loop.create_task(self.clear_pm_activity(message.prefix.nick, delay=5))
            return await self.send_private(user=message.prefix.nick, message=self.reply_message)

        # if destination is a channel call handler
        if message.parameters[0][0] == '#':
            channel = message.parameters[0][1:].lower()

            # if user writes in a channel, update activity
            if message.command == 'PRIVMSG':
                self.activity[channel][message.prefix.nick] = datetime.now(timezone.utc)

            if channel in self.channels and message.command in self.handlers[channel]:
                return await self.handlers[channel][message.command](connection, message)

    async def default_privmsg_handler(self, connection, message):
        # lowercase channel / username
        message.parameters[0] = message.parameters[0].lower()

        # check if channel allows commands
        if len(message.parameters[1]) and message.parameters[1][0] == '!':
            if not self.commands[message.parameters[0][1:]]:
                return self.logger.warning(
                    f' * Ignoring command in {message.parameters[0]} from {message.prefix.nick}: {message.parameters[1]}')

        # handle actions
        if message.parameters[1][:7] == '\x01ACTION':
            message.parameters[1] = f'~ {message.prefix.nick} {message.parameters[1][8:-1]} ~'
            # @ngrfisk you could check for "\x01ACTION is joining a game" or "\x01ACTION is hosting a game"
            return self.logger.warning(
                f' * Ignoring action in {message.parameters[0]} from {message.prefix.nick}: {message.parameters[1]}')

        # process PRIVMSG
        channel = message.parameters[0][1:].lower()
        sender = message.prefix.nick
        message = message.parameters[1]
        snooper = None

        # if user is sending from web snoop, then we could still match avatar
        if sender == self.snooper:
            snooper = sender
            match = re.match(r'^(?P<sender>.*?)>\s(?P<message>.*)$', message)
            sender = match.group('sender')
            message = match.group('message')

        # ignore messages from users on ignore list
        if sender in self.ignore:
            return self.logger.warning(f' * Ignored WormNET message from {sender}.')

        await self.forward_message(irc_channel=channel, sender=sender, message=message, snooper=snooper)
