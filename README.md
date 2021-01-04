# armabuddy
Barely functional bi-directional bridge between WormNET and Discord.

To start bot:
python bot.py >> log 2>&1 &

Required non-default Python modules:
 * discord.py
 * aiohttp
 * async-irc

### BOT SETTINGS ###
Settings is located in a big silly dict inside bot.py.
```py
settings = {
  'gamelist_urls': [
    'http://wormnet1.team17.com/wormageddonweb/GameList.asp?Channel=AnythingGoes',
    'http://wormnet.net/wormageddonweb/GameList.asp?Channel=AnythingGoes'
  ],
  'wormnet_host': 'wormnet1.team17.com',
  'wormnet_port': 6667,
  # wormnet nickname
  'wormnet_user': 'Discord',
  # password neeeded to enter wormnet, stolen from great snooper
  'wormnet_pass': 'ELSILRACLIHP',
  # messages coming from this nickname will be handled to appear as originating from snooper user
  'wormnet_snooper': 'WebSnoop',
  # when getting a PM it will automatically reply with this message
  'wormnet_message': (
    'This is a bot. '
    'I forward messages between Discord and WormNet. '
    'Feel free to join https://discord.gg/UBRBhk6 to meet all other wormers on discord!'
  ),
  # dict containing channels to join on wormnet
  # commands decide if you want to show messages prefixed with !
  # handlers decide which bot function to call when recieving a command from WormNet
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
  # any nicknames to be ignored, and for what reason
  'wormnet_ignore': {
    'WormsLeague': 'Spammer.',
    'CorujaBOT': 'League spammer.'
  },
  #discord bot token
  'discord_token': '',
  # guilds that will have bot enabled on them
  'discord_guilds': {
    # 'discord-guild': {}
    'Worms Armageddon ?': {
      # which discord channel to put gamelist, None if not enabled
      # (will still poll gamelist hosts, oops)
      'gamelist': 'open-games',
      # bi-directional link between channels
      #'discord-channel': 'irc-channel',
      'channels': {
        'anythinggoes': 'anythinggoes',
        'help': 'help'
      }
    }
  }
}
```
