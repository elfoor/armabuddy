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
сlass WA_Settings():
    # GAMELIST
    WA_Gamelist = {
        'interval': 15,  # WormNET game list query interval in seconds.
        'urls': [
            'http://wormnet1.team17.com/wormageddonweb/GameList.asp?Channel=AnythingGoes',  # T17 WormNET
            'http://wormnet.net/wormageddonweb/GameList.asp?Channel=AnythingGoes'  # Community server
        ]
    }

    WA_IRC = {
        'hostname': 'wormnet1.team17.com',
        'port': 6667,
        'username': 'Discord',
        'password': 'PHILCARLISLE'[::-1],
        'snooper': 'WebSnoop',
        'reply_message': 'This is a bot. I forward messages between Discord and WormNet. Feel free to'
                         ' join https://discord.gg/UBRBhk6 to meet all other wormers on discord!',
        'channels': ['anythinggoes', 'help'],
        'ignore': [  # WormNAT usernames who's messages should not be forwarded to discord
            'WormsLeague',  # Spammer
            'CorujaBOT'     # League spammer
        ]
    }

    # DISCORD
    WA_Discord = {
        'token': '[discord-token]',
        'guilds': {
            # Worms Armageddon (formally Dōjō)
            416225356706480128: {  # Discord Server ID
                'gamelist': 783363290557579305,  # Discord channel ID to add the game list embed to
                'channels': {
                    783002654501634058: 'anythinggoes',  # Discord channel ID that will mirror WormNAT AnythingGoes channel
                    783362534451314718: 'help'  # Discord channel ID that will mirror WormNAT Help channel
                }
            },
            # TeamWormers take 2
            918454442079178813: {
                'gamelist': 918454442800607247,
                'channels': {
                    918454442800607246: 'anythinggoes',
                    983773668041703464: 'help'
                }
            }
        }
    }

```
