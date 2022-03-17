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
			416225356706480128: { # Worms Armageddon
				'gamelist': 783363290557579305,
				'channels': {
					783002654501634058: 'anythinggoes',
					783362534451314718: 'help'
				}
			},
			763838112198557766: { # TeamWormers
				'gamelist': 894304280352260138,
				'channels': {
          894304244335792178: 'anythinggoes'
        }
			}
		}
	}
