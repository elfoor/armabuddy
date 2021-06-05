class WA_Settings():
	# GAMELIST
	WA_Gamelist = {
		'interval': 15,
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
		'snooper': 'WebSnoop',
		'reply_message': 'This is a bot. I forward messages between Discord and WormNet. Feel free to join https://discord.gg/UBRBhk6 to meet all other wormers on discord!',
		'channels': ['anythinggoes', 'help'],
		'ignore': [
			'WormsLeague', # spammer
			'CorujaBOT'    # League spammer
		]
	}

	# DISCORD
	WA_Discord = {
		'token': '[discord-token]',
		'guilds': {
			'Worms Armageddon': {
				'gamelist': 'open-games',
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
