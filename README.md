# armabuddy
Barely functional bi-directional bridge between WormNET and Discord.

To start bot:
python bot.py >> log 2>&1 &

Required non-default Python modules:
 * discord.py
 * aiohttp
 * async-irc

### BOT SETTINGS ###
Settings is located inside wa_settings.py
```py
class WA_Settings():
	# GAMELIST
	WA_Gamelist = {
		# how often to update gamelists
		'interval': 15,
		# which urls to fetch gamelist from
		'urls': [
			'http://wormnet1.team17.com/wormageddonweb/GameList.asp?Channel=AnythingGoes',
			'http://wormnet.net/wormageddonweb/GameList.asp?Channel=AnythingGoes'
		]
	}

	WA_IRC = {
		'hostname': 'wormnet1.team17.com',
		'port': 6667,
		'username': 'Discord',
		'password': 'ELSILRACLIHP',
		# messages originating from this user will be handled as if coming from original sender
		'snooper': 'WebSnoop',
		# message sent if recieving a PM
		'reply_message': 'This is a bot. I forward messages between Discord and WormNet. Feel free to join https://discord.gg/UBRBhk6 to meet all other wormers on discord!',
		# channels to join on wormnet
		'channels': ['anythinggoes', 'help'],
		# users to ignore
		'ignore': [
			'WormsLeague', # spammer
			'CorujaBOT'    # League spammer
		]
	}

	# DISCORD
	WA_Discord = {
		'token': '[discord-token]',
		'guilds': {
			# discord guild name
			'Worms Armageddon': {
				# channel to put game list inside
				'gamelist': 'open-games',
				# channels to enable forwarding between. discord channel -> irc channel
				'channels': {
					'anythinggoes': 'anythinggoes',
					'help': 'help'
				}
			},
			'Worms United': {
				'gamelist': 'open-games',
				'channels': {}
			}
		}
	}
```
