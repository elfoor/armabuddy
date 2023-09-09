# armabuddy
Barely functional bi-directional bridge between WormNET and Discord.

To start bot:
python bot.py >> log 2>&1 &

Required non-default Python modules:
 * [discord.py](https://pypi.org/project/discord.py/)
 * [async-irc](https://pypi.org/project/async-irc/)

### BOT SETTINGS ###
Settings is located inside wa_settings.py
```py
class WA_Settings:
    # GAMELIST
    WA_Gamelist = {
        'interval': 10,  # WormNET game list query interval in seconds.
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
        'help_message': r'\bHelp is also available from the W:A community via Discord. _ _ _ _ _ _ _ _ _ _ _ _ _'
                        r' \BYou can join the \wWorms Armageddon \Bserver here:'
                        r' \Rhttps://\rdiscord.gg/UBRBhk6'.replace('_', '\N{NO-BREAK SPACE}'),
        'channels': ['anythinggoes', 'help'],
        'ignore': [  # WormNET usernames whose messages should not be forwarded to discord
            'WormsLeague',  # Spammer
            'CorujaBOT'     # League spammer
        ]
    }

    # DISCORD
    WA_Discord = {
        'token': '[discord-token]',
        'http_redir_url': 'http://redirect-http-to-wa.com:17012',
        'embed_color': 0xffa300,
        'embed_icon': 'https://cdn.discordapp.com/emojis/501802399565086720.png?size=32',
        'guilds': {
            # Worms Armageddon (formally Dōjō)
            416225356706480128: {  # Discord Server ID
                'disable_forwarding': False,  # If true: Only reads WormNET messages, disables sending from this server
                'gamelist': 783363290557579305,  # Discord channel ID to add the game list embed to
                'channels': {
                    783002654501634058: 'anythinggoes',  # Discord channel ID that will mirror WormNET AnythingGoes channel
                    783362534451314718: 'help'  # Discord channel ID that will mirror WormNET Help channel
                },
                'wormnet_channel_settings': {
                    'anythinggoes': 'Pf,Be',
                    'help': 'Tf'
                }
            }
        }
    }

    # HTTP Redir server
    WA_HTTP_Redir = {
        'host_ip': '0.0.0.0',
        'host_port': 17012,
        'server_headers': {'Server': ''}
    }
```
