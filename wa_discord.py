# wa_discord.py
import asyncio
import logging
import re
from datetime import datetime, timezone

from wa_flags import WA_Flags, COUNTRY_CODES
import discord
discord.VoiceClient.warn_nacl = False


class WA_Discord(discord.Client):
    def __init__(self, token: str, guilds: dict):
        # internal properties
        self.token = token  # discord token used for authenticating bot
        # dict containing settings on which guilds and channels we need to make sure exist
        self.settings = guilds
        self.guild_list = {}  # dict that will contain all references to channels and guilds
        self.logger = logging.getLogger('WA_Logger')
        self._intents = discord.Intents.default()
        self._intents.members = True
        self._intents.message_content = True
        self.prepared = False
        self.irc_reference = None
        self.forward_message = lambda x: x

        # embed config
        self.embed_gamelist_title = 'Currently active games in #AnythingGoes'
        self.embed_color = 0xffa300
        self.embed_icon = 'https://cdn.discordapp.com/emojis/501802399565086720.png?size=32'
        self.embed_footer = 'List last refreshed at'
        self.embed_default_flag = WA_Flags['49']
        self.embed_public_game = ':unlock:'
        self.embed_private_game = ':closed_lock_with_key:'
        self.embed_snooper_icon = '<:snooper:750119141423448186>'
        self.embed_no_host = '*There are currently no games hosted on WormNET..* <:sadworm:883155422675087452>'
        self.embed_no_users = '*There are currently no users online on WormNET, something is probably horribly wrong.'

        # static messages
        self.bot_message_setup = 'I am trying to be a good bot, please bear with me while until I find all the cogs and gears!'
        self.bot_down_message = "I am sick right now and can't show you the game list at this moment."

        self.required_permissions = (
            'read_messages',  # view_channel, must be checked first
            'read_message_history',  # to find pinned messages
            'send_messages',  # to get discord.py to test for embed_links permission properly, must be above embed_links
            'embed_links',  # to add self.embed_icon image link
            'manage_webhooks'
        )
        self.required_setup_permissions = (  # only needed once when setting up initial pinned messages
            'send_messages',  # to create initial messages
            'manage_messages'  # to pin initial messages
        )
        super().__init__(intents=self._intents)

    # HELPER FUNCTIONS #

    async def run(self):
        if self.is_closed() and self.is_ready():
            raise Exception(' * Unable to start bot.')

        self.logger.warning(' * Starting bot.')
        await self.start(self.token)

    async def stop(self):
        self.logger.warning(' * Stopping bot.')
        await self.close()

    # create an embed from WA_Gamelist response
    async def create_gamelist(self, games: list):
        embed = discord.Embed(title=self.embed_gamelist_title, colour=self.embed_color,
                              timestamp=datetime.now(timezone.utc))
        # embed.set_thumbnail(url=self.embed_icon) # thumbnail does not fit if we want proper list
        embed.set_footer(text=self.embed_footer, icon_url=self.embed_icon)
        field = ''
        for game in games:
            append = flag = ''

            if game['packed_flag_id'] != '0':
                # attempt to unpack ISO 3166-1 alpha-2 country code from LOWORD of last field of game response
                flag_bytes = (int(game['packed_flag_id']) & 0xFFFF).to_bytes(2, 'little')
                if all(ord('A') <= char <= ord('Z') for char in flag_bytes):
                    flag = f':flag_{flag_bytes.decode("ascii").lower()}:'

            if not flag:
                flag = WA_Flags.get(game['country'], self.embed_default_flag)

            append += self.embed_private_game if game['private'] == '1' else self.embed_public_game
            append += f'{discord.utils.escape_markdown(game["title"])} \n<wa://{game["host"]}?Scheme=Pf,Be&ID={game["gameid"]}>\n'
            append += f'Hosted by: {flag} {discord.utils.escape_markdown(game["user"])}\n\n'

            # fields can't be longer than 1024 characters, so better make sure we don't surpass limit..
            if len(field) + len(append) >= 1024:
                embed.add_field(name='Games', value=field, inline=False)
                field = ''
            field += append

        # if field is empty at this point there shouldn't be any open games, make sure we put placeholder description instead..
        if len(field) <= 0:
            embed.description = self.embed_no_host
        else:
            embed.add_field(name='Games', value=field, inline=False)
        return embed

    # make sure all our configured Guild(s) exist
    async def check_guilds(self):
        for guild in self.guilds:
            # if guild id is equal to id from settings file
            if guild.id in self.settings:
                self.logger.warning(f' * Found guild with name "{guild.name}"!')
                self.guild_list[guild.id] = {
                    'guild': guild,
                    'channels': self.settings[guild.id]['channels'],
                    'gamelist': self.settings[guild.id]['gamelist']
                }
            else:
                self.logger.warning(f' ! Could not find guild "{guild.name}" in settings.')

    async def check_permission_missing(self, channel, guild, required_permissions):
        for permission_name, permission_active in channel.permissions_for(guild.me):
            if permission_name in required_permissions and not permission_active:
                self.logger.warning(f' ! Missing "{permission_name}" permission for "#{channel.name}"'
                                    f' in guild "{guild.name}"! Skipping channel.')
                return True
        return False

    # make sure all Guild(s) have the TextChannel(s) we have set up, with correct permissions, skip channels that don't
    async def check_channels(self):
        # for every guild we have setup
        for settings in self.guild_list.values():
            guild = settings['guild']
            for channel in guild.text_channels:
                if channel.id in settings['channels']:
                    if await self.check_permission_missing(channel, guild, self.required_permissions):
                        del settings['channels'][channel.id]
                        continue

                    self.logger.warning(f' * Found message forwarding channel #{channel.name} in guild "{guild.name}"!')
                    settings['channels'][channel.id] = {
                        'channel': channel,
                        'forward': settings['channels'][channel.id],
                        'webhook': {},
                        'message': {}
                    }

                if settings['gamelist'] and channel.id == settings['gamelist']:
                    if await self.check_permission_missing(channel, guild, self.required_permissions):
                        settings['gamelist'] = 0
                        continue

                    self.logger.warning(f' * Found game list channel #{channel.name} in guild "{guild.name}"!')
                    settings['gamelist'] = {
                        'channel': channel,
                        'message': {}
                    }

            for channel_id, values in list(settings['channels'].items()):
                if type(values) != dict:
                    self.logger.warning(f' ! Could not find the message forwarding channel with id {channel_id}'
                                        f' in guild "{guild.name}". Skipping channel.')
                    del settings['channels'][channel_id]

            if settings['gamelist'] and type(settings['gamelist']) != dict:
                self.logger.warning(f' ! Could not find the game list channel with id {settings["gamelist"]}'
                                    f' in guild "{guild.name}". Skipping channel.')
                settings['gamelist'] = 0

    # looks for the first pinned message from this bot to use as a game list
    async def check_gamelists(self):
        for settings in self.guild_list.values():
            if settings['gamelist']:
                guild = settings['guild']
                channel = settings['gamelist']['channel']

                for message in await channel.pins():
                    if message.author == self.user:
                        settings['gamelist']['message'] = message

                if not isinstance(settings['gamelist']['message'], discord.Message):
                    if await self.check_permission_missing(channel, guild, self.required_setup_permissions):
                        settings['gamelist'] = 0
                        continue

                    self.logger.warning(
                        f' ! No pinned game list belonging to "{self.user.name}" in #{channel.name} on "{guild.name}".')
                    settings['gamelist']['message'] = await channel.send(self.bot_message_setup)
                    await settings['gamelist']['message'].pin()
                    self.logger.warning(f' * Created and pinned game list in #{channel.name} on "{guild.name}".')
                else:
                    self.logger.warning(f' * Found pinned game list in #{channel.name} on "{guild.name}"!')

    # make sure webhooks exist in all forwarding channels
    async def check_webhooks(self):
        for settings in self.guild_list.values():
            guild = settings['guild']
            for channel_settings in settings['channels'].values():
                channel = channel_settings['channel']

                for webhook in await channel.webhooks():
                    if webhook.name == self.user.name:
                        channel_settings['webhook'] = webhook
                        self.logger.warning(
                            f' * Found webhook with name {self.user.name} in #{channel.name} on "{guild.name}"!')
                        break

                if not channel_settings['webhook']:
                    self.logger.warning(
                        f' ! Could not find webhook with name {self.user.name} in #{channel.name} on "{guild.name}"!')
                    channel_settings['webhook'] = await channel.create_webhook(name=self.user.name,
                                                                               avatar=await self.user.avatar.read())
                    self.logger.warning(
                        f' * Created webhook with name {self.user.name} in #{channel.name} on "{guild.name}"!')

    async def check_userlists(self):
        for settings in self.guild_list.values():
            guild = settings['guild']
            for channel_settings in list(settings['channels'].values()):
                channel = channel_settings['channel']

                if settings['gamelist'] and settings['gamelist']['channel'] == channel:
                    raise Exception(f'Can\'t have both user list and game list in #{channel.name} on'
                                    f' "{guild.name}", check configuration.')

                for message in await channel.pins():
                    if message.author == self.user:
                        settings['channels'][channel.id]['message'] = message

                if not isinstance(channel_settings['message'], discord.Message):
                    if await self.check_permission_missing(channel, guild, self.required_setup_permissions):
                        del settings['channels'][channel.id]
                        continue

                    self.logger.warning(f' ! No pinned user list belonging to "{self.user.name}"'
                                        f' in #{channel.name} on "{guild.name}".')
                    settings['channels'][channel.id]['message'] = await channel.send(self.bot_message_setup)
                    await channel_settings['message'].pin()
                    self.logger.warning(f' * Created and pinned user list in #{channel.name} on "{guild.name}".')
                else:
                    self.logger.warning(f' * Found pinned user list in #{channel.name} on "{guild.name}"!')

    # edits pinned message containing game lists
    async def update_gamelists(self, **kwargs):
        if not self.prepared:  # not safe to interact with discord before initialization is complete
            return self.logger.warning(' ! Attempted to forward message to Discord before initialization'
                                       ' was fully complete.')

        for settings in self.guild_list.values():
            guild = settings['guild']
            if settings['gamelist']:
                channel = settings['gamelist']['channel']
                await settings['gamelist']['message'].edit(**kwargs)
                self.logger.warning(f' * Updated pinned game list in #{channel.name} on "{guild.name}".')

    async def get_sorted_user_entries(self, all_users):
        # Separate users and snoopers and add snooper rank/flag to each and sort for display.
        # Imitate WA flag behaviours such as FlagID taking precedence over country code

        users, snoop_users = [], []
        for username, realname_parameters in all_users.items():
            # Treat ChanServ as a snooper to get it sorted at the bottom with the other bots
            if username == 'ChanServ':
                snoop_users.append((self.embed_snooper_icon, username))
                continue

            if 'snoop' in realname_parameters.lower():
                snoop_users.append((self.embed_snooper_icon, username))
                continue

            realname_parameters = realname_parameters.split(' ')
            if len(realname_parameters) < 4:
                users.append((f'{WA_Flags["49"]}', username))
                continue

            # rank id 13 (snooper), as is, or via a 32-bit unsigned integer overflow to 13 (ProSnooper buddy fix thing)
            if realname_parameters[1] in ('13', '4294967309'):
                snoop_users.append((self.embed_snooper_icon, username))
                continue

            try:
                flag_id = int(realname_parameters[0])
            except ValueError:
                users.append((f'{WA_Flags["49"]}', username))
                continue

            if flag_id < 49:
                users.append((f'{WA_Flags.get(str(flag_id), "49")}', username))
                continue

            if flag_id == 49 and (country_code := realname_parameters[2]) in COUNTRY_CODES:
                users.append((f':flag_{country_code.lower()}:', username))
            else:
                users.append((f'{WA_Flags["49"]}', username))

        users.sort(key=lambda user_entry: user_entry[1].lower())
        snoop_users.sort(key=lambda user_entry: user_entry[1].lower())
        return users, snoop_users

    # edits pinned messages containing user list for given channel
    async def update_userlists(self, channels: dict, interval=5):
        await asyncio.sleep(interval)

        # not safe to interact with discord before initialization is complete
        while not self.prepared:
            self.logger.warning(' ! Attempted to update userlist on Discord before initialization was fully complete.')
            await asyncio.sleep(interval)

        while True:
            for channel, all_users in channels.items():
                userlist = discord.Embed(colour=self.embed_color, timestamp=datetime.now(timezone.utc))
                userlist.set_footer(text=self.embed_footer, icon_url=self.embed_icon)

                if not all_users or not len(all_users):
                    userlist.description = self.embed_no_users
                else:
                    users, snoop_users = await self.get_sorted_user_entries(all_users)

                    field = ''
                    title = (f'{len(users) + len(snoop_users)} online in #{channel}\n'
                             f'({len(users)} users and {len(snoop_users)} snoopers)')

                    for user_type in users, snoop_users:
                        for user_icon, username in user_type:
                            append = f'{user_icon}\N{EM SPACE}{discord.utils.escape_markdown(username)}\n'

                            if len(field) + len(append) >= 1024:
                                userlist.add_field(name=title, value=field, inline=False)
                                title = ''  # clear title to prevent it repeating for every field if length over max
                            field += append

                        if len(field) <= 0:
                            userlist.description = self.embed_no_host
                        else:
                            userlist.add_field(name=title, value=field, inline=False)

                        title = field = ''

                for settings in self.guild_list.values():
                    for channel_settings in settings['channels'].values():
                        if channel == channel_settings['forward']:
                            await channel_settings['message'].edit(content=None, embed=userlist)

            await asyncio.sleep(interval)

    # forwards messages to channel using webhooks, if nickname exist on discord it will use their avatar
    async def send_message(self, irc_channel: str, sender: str, message: str, action: bool = False, snooper: str = None,
                           origin: discord.TextChannel = None):

        # not safe to interact with discord before initialization is complete
        if not self.prepared:
            return self.logger.warning(' ! Attempted to forward message to Discord before'
                                       ' initialization was fully complete.')

        # ignore blank lines, since discord won't let me post a message with only whitespaces.
        if not message or message.isspace():
            return self.logger.warning(f' * Ignoring blank WormNET message from {sender} in #{irc_channel}.')

        # escape discord mentions and markdown
        message = discord.utils.escape_mentions(message)
        message = discord.utils.escape_markdown(message)

        # suppress invite links with http strip + `` wrap (discord mobile workaround), suppress other links with <> wrap
        message = re.sub(r'https?://(discord.gg/\S+)', r'`\g<1>`', message, flags=re.MULTILINE | re.IGNORECASE)
        message = re.sub(r'(https?://\S+)', r'<\g<1>>', message, flags=re.MULTILINE | re.IGNORECASE)

        # actions need to be italics
        if action:
            message = '*' + message + '*'

        # loop through every saved guild and every saved channel and forward message only to specific channels
        for settings in self.guild_list.values():
            guild = settings['guild']
            for channel_settings in settings['channels'].values():
                channel = channel_settings['channel']
                if channel_settings['forward'] == irc_channel and origin != channel_settings['channel']:

                    # log type of message, and message contents
                    if origin:
                        self.logger.warning(f' * Forwarding message by {sender} on Discord #{origin.name} on'
                                            f' "{origin.guild.name}" to #{channel.name} on "{guild.name}": {message}')
                    else:
                        self.logger.warning(f' * Forwarding message by {sender} on WormNET #{irc_channel} to '
                                            f'#{channel.name} on "{guild.name}": {message}')

                    # then proceed to find user avatar if possible, and post it using the webhook
                    member = guild.get_member_named(sender)
                    username = sender if not snooper else f'{sender} ({snooper})'
                    avatar_url = member.display_avatar if isinstance(member, discord.Member) else None
                    # workaround douchecord being possessive with their name
                    username = re.sub('discord', 'Disc\N{CYRILLIC SMALL LETTER O}rd', username, flags=re.IGNORECASE)
                    # workaround triple backtick issue
                    username = username.replace('```', '\N{MODIFIER LETTER GRAVE ACCENT}' * 3)
                    await channel_settings['webhook'].send(content=message, username=username, avatar_url=avatar_url)

    # find forwarding channel name as string
    async def find_forward_channel(self, channel: discord.TextChannel):
        for guild_name, guild_info in self.guild_list.items():
            for channel_name, channel_info in guild_info['channels'].items():
                if channel_info['channel'] == channel and guild_info['guild'] == channel.guild:
                    return channel_info['forward']
        return False

    # EVENT LISTENERS #

    async def on_message(self, message):
        if message.author == self.user or not len(message.clean_content) or message.webhook_id:
            return

        # forward to all other discord servers
        irc_channel = await self.find_forward_channel(channel=message.channel)
        sender = message.author.name
        snooper = 'Other Discord'
        await self.send_message(irc_channel=irc_channel, sender=sender, message=message.content, snooper=snooper,
                                origin=message.channel)

        # finally forward to IRC
        for settings in self.guild_list.values():
            guild = settings['guild']
            for channel_settings in settings['channels'].values():
                channel = channel_settings['channel']
                if channel == message.channel and guild == message.guild:
                    await self.forward_message(
                        guild=guild.name,
                        origin=channel.name,
                        channel=channel_settings['forward'],
                        message=f'{message.author.display_name}> {message.clean_content}'
                    )

    # catch all errors and propagate this error to the loop exception handler
    async def on_error(self, event):
        raise

    async def on_ready(self):
        await self.check_guilds()
        await self.check_channels()
        await self.check_gamelists()
        await self.check_userlists()
        await self.check_webhooks()

        for settings in list(self.guild_list.values()):
            guild = settings['guild']
            if not settings['channels'] and not settings['gamelist']:
                self.logger.warning(f' ! No channels setup for guild {guild.name}! Skipping guild.')
                del self.guild_list[guild.id]

        if not self.guild_list:
            raise Exception('No guilds configured!')

        self.prepared = True
        self.logger.warning(f' * {self.user.name} has been fully initialized!')

    async def on_disconnect(self):
        self.logger.warning(f' ! {self.user.name} has disconnected from Discord!')
        # raise Exception(f'{self.user.name} has disconnected from Discord!')

    async def on_connect(self):
        self.logger.warning(f' * {self.user.name} has connected to Discord!')
