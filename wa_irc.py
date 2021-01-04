import asyncio
import logging
import re
from asyncirc.protocol import IrcProtocol
from asyncirc.server import Server
from irclib.parser import Message
from wa_encoder import WA_Encoder

class WA_IRC():
	def __init__(self, *args, **kwargs):

			if not kwargs:
				raise ValueError('Missing required keyword arguments.')

			if not 'nickname' in kwargs or not isinstance(kwargs['nickname'], str):
				raise ValueError('Invalid nickname.')

			if not 'wormnet' in kwargs or not isinstance(kwargs['wormnet'], str):
				raise ValueError('Invalid WormNet server.')

			if not 'channels' in kwargs or not isinstance(kwargs['channels'], dict):
				raise ValueError('Invalid WormNet channel dict.')

			if not 'port' in kwargs or not isinstance(kwargs['port'], int):
				raise ValueError('Invalid WormNet port.')

			if not 'loop' in kwargs or (not isinstance(kwargs['loop'], asyncio.SelectorEventLoop) and not isinstance(kwargs['loop'], asyncio.ProactorEventLoop)):
				raise ValueError('Invalid event loop.')

			self.logger = logging.getLogger('WA_Logger')
			self.wormnet = kwargs.pop('wormnet')
			self.nickname = kwargs.pop('nickname')
			self.channels = dict.fromkeys(kwargs.pop('channels').keys())
			self.port = kwargs.pop('port')
			self.password = kwargs.pop('password', None)
			self.is_ssl = kwargs.pop('is_ssl', False)
			self.loop = kwargs.pop('loop')
			self.transcode = False
			self.reconnect_delay = 30
			self.server = Server(self.wormnet, self.port, self.is_ssl, password = self.password)

			# register handlers for every needed internal
			self.connection = IrcProtocol([self.server], self.nickname, loop=self.loop)
			self.connection.register_cap('userhost-in-names')
			self.connection.register('*', self.log)
			self.connection.register('002', self.decide_transcode)
			self.connection.register('376', self.join_channels)
			self.connection.register('JOIN', self.handle_entry)
			self.connection.register('PART', self.handle_entry)
			self.connection.register('QUIT', self.handle_entry)
			self.connection.register('353', self.handle_entry)

			# horrrible horrible hack for a horrible horrible library
			IrcProtocol.connection_lost = __class__.connection_lost

	async def connect(self):
		# begin connection
		self.logger.warning(' * Connecting to Wormnet.')
		if await self.connection._connect(server = self.server):
			self.logger.warning(' * Connected to Wormnet.')

		# wait for endo f MOTD to signal proper connection
		if not await self.connection.wait_for('376', timeout = self.reconnect_delay):
			self.logger.warning(f' ! Unable to connect to properly WormNet, attempting to reconnect.')
			return await self.connect()

		# wait until we lose connection
		while self.connection._connected:
			await asyncio.sleep(1)

		# if connection ha dies, attempt to restart it
		self.logger.warning(f' ! Disconnected from WormNet, attempting to reconnect in {self.reconnect_delay} seconds.')
		await asyncio.sleep(self.reconnect_delay)
		return await self.connect()

	async def decide_transcode(self, conn, message):
		# check if this is the community server, if so, disable transcoding of messages by monkey-patching IrcProtocol.data_received
		if len(message.parameters) >= 2 and 'ae.net.irc.server/WormNET' in message.parameters[1]:
			self.logger.warning(' * Disabled transcoding for WormNet messages.')
			IrcProtocol.data_received = __class__.transcode_off
			self.transcode = False
		else:
			self.logger.warning(' * Enabled transcoding for WormNet messages.')
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
			raw_line = WA_Encoder.decode(raw_line)
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
		self.logger.info(' * IRC_RAW' + str(message))

	async def handle_entry(self, conn, message):
		channel = message.parameters[0][1:].lower()
		if message.command == 'JOIN': # add user to channel set if joining
			if channel in self.channels:
				self.channels[channel].add(message.prefix.nick)
		elif message.command == 'PART': # remove user from channel set if parting
			if channel in self.channels:
				self.channels[channel].discard(message.prefix.nick)
		elif message.command == 'QUIT': # remove user from all channel sets if quitting
			for channel in self.channels:
				if self.channels[channel]:
					self.channels[channel].discard(message.prefix.nick)
		elif message.command == '353':
			# strip any modes from users, should not be set on WormNet, but will make testing a pain on regular networks
			no_modes = message.parameters[3].translate({ord(i): None for i in '@+$%'})
			users = no_modes.split()
			channel = message.parameters[2][1:].lower()
			for user in users:
				self.channels[channel].add(user.split('!')[0])

	async def join_channels(self, conn, message):
		for channel_name, settings in self.channels.items():
			# create new set containing user list
			self.channels[channel_name] = set(())
			self.logger.warning(f' * Joining WormNet channel: #{channel_name}!')
			self.connection.send(f'JOIN #{channel_name}')

			# give server a few seconds to give us NAMES, if none has been recieved after timeout propagate error
			result = await self.connection.wait_for('366', timeout = 30)
			if result == None:
				raise Exception(f'Never recieved NAMES after joining WormNet channel #{channel}.')

	async def forward_message(self, guild, origin, channel, message):
		# strip everything after \n to avoid sneaky user sending multiple commands in single string
		message = message.split('\n')[0]
		message = f'PRIVMSG #{channel} :{message}'

		# keep message under 250 characters at least, in reality max length is 512
		message = (message[:250] + '[...]') if len(message) > 250 else message
		self.logger.warning(f' * Forwarding message from #{origin} on "{guild}" to WormNet #{channel}: {message}')
		await self.transport_write(message)

	async def forward_private(self, user, message):
		# strip everything after \n to avoid sneaky user sending multiple commands in single string
		message = message.split('\n')[0]
		message = f'PRIVMSG {user} :{message}'

		self.logger.warning(f' * Forwarding PM to WormNet user {user}: {message}')
		await self.transport_write(message)

	async def transport_write(self, message):
		if self.connection._connected:
			message = message + '\r\n'
			message = WA_Encoder.encode(message) if self.transcode == True else message.encode()
			self.connection._transport.write(message)
		else:
			self.logger.warning(' ! Could not forward message due to connection to IRC being down!')