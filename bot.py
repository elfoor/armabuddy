import asyncio
import traceback
import logging
import re
from datetime import datetime
from wa_irc import WA_IRC
from wa_gamelist import WA_Gamelist
from wa_discord import WA_Discord

""" FUNCTIONS """
def fatal_handler(loop, context):
	exception = context.get('exception')
	logger.critical(' ! ' + str(exception))
	logger.critical(' ! Encountered FATAL error. Shutting down.\n')
	traceback.print_exception(type(exception), exception, exception.__traceback__)
	loop.stop()

async def userlist_update(interval = 7):
	while True:
		await asyncio.sleep(interval)
		for channel, users in irc.channels.items():
			await discord.update_userlists(channel = channel, users = users)

async def gamelist_update(interval = 15):
	fail = 0
	while True:
		try:
			await asyncio.sleep(interval)
			result = await gamelist.fetch()
			embed = await discord.create_gamelist(result)
			await discord.update_gamelists(content = None, embed = embed)
			fail = 0
		except Exception as e:
			traceback.print_exception(type(e), e, e.__traceback__)
			fail += 1
			logger.warning(f' ! Fetching gamelist has failed {fail} times in a row.')
			logger.warning(' ! ' + str(e))
			if fail >= 3:
				logger.warning(f' ! Fetching gamelist has failed the maximum allowed times in a row.')
				raise


async def irc_handle_command(connection, message):
	# ignore commands triggered by self
	if message.prefix.nick == irc.nickname:
		return

	# if destination is a channel call handler
	if message.parameters[0][0] == '#':
		channel = message.parameters[0][1:].lower()
		if channel in settings['wormnet_channels'] and message.command in settings['wormnet_channels'][channel]['handlers']:
			return await settings['wormnet_channels'][channel]['handlers'][message.command](connection, message)

	# reply to all PM with predefined phrase
	elif message.parameters[0][0] != '#' and message.command == 'PRIVMSG':
		logger.warning(f' * Recieved PM on WormNet from {message.prefix.nick}: {message.parameters[1]}')
		return await irc.forward_private(user = message.prefix.nick, message = settings['wormnet_message'])


async def irc_privmsg_handler(connection, message):
	# lowercase channel / username
	message.parameters[0] = message.parameters[0].lower()

	# check if channel allows commands
	if len(message.parameters[1]) and message.parameters[1][0] == '!':
		if not settings['wormnet_channels'][message.parameters[0][1:]]['commands']:
			return logger.warning(f' * Ignoring command in {message.parameters[0]} from {message.prefix.nick}: {message.parameters[1]}')

	# handle actions
	if message.parameters[1][:7] == '\x01ACTION':
		message.parameters[1] = '~ ' + message.prefix.nick + ' ' + message.parameters[1][8:-1] + ' ~'
		# @ngrfisk you could check for "\x01ACTION is joining a game" or "\x01ACTION is hosting a game"
		return logger.warning(f' * Ignoring action in {message.parameters[0]} from {message.prefix.nick}: {message.parameters[1]}')

	# process privmsg
	channel = message.parameters[0][1:].lower()
	sender = message.prefix.nick
	message = message.parameters[1]
	snooper = None

	# if user is sending from websnoop, then we could still match avatar
	if sender == settings['wormnet_snooper']:
		snooper = sender
		match = re.match(r'^(?P<sender>.*?)>\s(?P<message>.*)$', message)
		sender = match.group('sender')
		message = match.group('message')

	# ignore messages from users on ignore list
	if settings['wormnet_ignore'] and sender in settings['wormnet_ignore']:
		return logger.warning(f' * Ignoring message from {sender} with reason: {settings["wormnet_ignore"][sender]}')

	await discord.forward_message(channel = channel, sender = sender, message = message, snooper = snooper)


async def irc_entry_help_handler(connection, message):
	sender = message.prefix.nick
	# only write join / par messages if user has written in #help
	if sender in help_activity_dict:
		# if parting, always show else only if written in the last {help_activity_limit} minutes
		if (datetime.now() - help_activity_dict[sender]).total_seconds() <= help_activity_limit * 60 or message.command == 'PART':
			channel = message.parameters[0][1:].lower()
			message = sender + ' has ' + message.command.lower() + 'ed the channel!'
			return await discord.forward_message(channel = channel, sender = sender, message = message, action = True)
		# if not parting or have not written in a while, remove user from activity list
		else:
			return help_activity_dict.pop(sender, None)


async def irc_privmsg_help_handler(connection, message):
	# pre-handle help chats to save activity for later comparison with part message
	help_activity_dict[message.prefix.nick] = datetime.now()
	return await irc_privmsg_handler(connection, message)


async def discord_handle_message(message):
	if message.author == discord.user or not len(message.clean_content) or message.webhook_id:
			return

	# forward to all other discord servers
	channel = await discord.find_forward_channel(channel = message.channel.id)
	sender = message.author.name
	snooper = 'Other Discord'
	await discord.forward_message(channel = channel, sender = sender, message = message.content, snooper = snooper, origin = message.channel.id)

	# finally forward to IRC
	for guild_name, guild_info in discord.guild_list.items():
		for channel_name, channel_info in guild_info['channels'].items():
			if channel_info['channel'] == message.channel and guild_info['guild'] == message.guild:
				await irc.forward_message(
					guild = guild_name,
					origin = channel_name,
					channel = channel_info['forward'],
					message = f'{message.author.display_name}> {message.clean_content}'
				)


""" MAIN """
try:

	### BOT SETTINGS ###
	settings = {
		'gamelist_urls': [
			'http://wormnet1.team17.com/wormageddonweb/GameList.asp?Channel=AnythingGoes',
			'http://wormnet.net/wormageddonweb/GameList.asp?Channel=AnythingGoes'
		],
		#'wormnet_host': 'wormnet.net',
		'wormnet_host': 'wormnet1.team17.com',
		'wormnet_port': 6667,
		'wormnet_user': 'Discord',
		'wormnet_pass': 'ELSILRACLIHP',
		'wormnet_snooper': 'WebSnoop',
		'wormnet_message': (
			'This is a bot. '
			'I forward messages between Discord and WormNet. '
			'Feel free to join https://discord.gg/UBRBhk6 to meet all other wormers on discord!'
		),
		'wormnet_channels': {
			'anythinggoes': {
				'commands': False,
				'handlers': {
					'PRIVMSG': irc_privmsg_handler
				}
			},
			'help': {
				'commands': True,
				'handlers': {
					'PRIVMSG': irc_privmsg_help_handler,
					'JOIN': irc_entry_help_handler,
					'PART': irc_entry_help_handler
				}
			}
		},
		'wormnet_ignore': {
			'WormsLeague': 'Spammer.',
			'CorujaBOT': 'League spammer.' # remove this
		},
		'discord_token': 'ODQ5MjY1NTA0Mjg3NTg4Mzgy.YLYqIg.q7A59F8pr4JrsFHyzXLk9etyBm0',
		'discord_guilds': {
			# guilds that will have bot enabled on them
			# 'discord-guild': {}
			817807686841663560: {
				# channel to put gamelist in, None if not enabled
				# 'gamelist: 'discord-channel',
				'gamelist': 849295916325535755,
				'channels': {
					# bi-directional link between channels
					#'discord-channel': 'irc-channel',
					849295935040651285: 'AnythingGoes',
					849295966523097098: 'Help'
				}
			},

				}
			}
		
	

	### GLOBALS SETUP ###
	help_activity_dict = {}
	help_activity_limit = 5 # minutes

	### LOGGING SETUP ###
	logger = logging.getLogger('WA_Logger')
	logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

	### ASYNCIO SETUP ###
	loop = asyncio.get_event_loop()
	loop.set_exception_handler(fatal_handler)

	### DISCORD SETUP ###
	discord = WA_Discord(forwarding = settings['discord_guilds'],	token = settings['discord_token'])
	discord.on_message = discord_handle_message
	loop.create_task(discord.run())

	### IRC SETUP ###
	irc = WA_IRC(nickname=settings['wormnet_user'], wormnet = settings['wormnet_host'], port = settings['wormnet_port'], channels = settings['wormnet_channels'], loop = loop, password = settings['wormnet_pass'])
	irc.connection.register('PRIVMSG', irc_handle_command)
	irc.connection.register('PART', irc_handle_command)
	irc.connection.register('JOIN', irc_handle_command)
	loop.create_task(irc.connect())

	### LIST SETUP ###
	gamelist = WA_Gamelist(gamelist_urls = settings['gamelist_urls'])
	loop.create_task(userlist_update())
	loop.create_task(gamelist_update())

	loop.run_forever() # this works, NICE!
except Exception as e:
	print(e)
