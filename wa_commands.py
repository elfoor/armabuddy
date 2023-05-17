import discord
import aiohttp
import json
import asyncio
from wa_wormnat_guide_poster import main as post_wormnat_guide
from wa_encoder import WA1252
from wa_settings_cgarz import WA_Settings
import logging


class WA_Commands:
    def __init__(self):
        # https://snoop.wormnet.net/data/initinfo and http://proxy.worms2d.info/data/schemes/schemes.xml
        self.SCHEME_IDS_NAMES = {
            1:  ('Battle Race', 'BR'),
            2:  ('Boom Race', 'Boom'),
            3:  ('Bungee Race',),
            4:  ('Jet Pack Race', 'Jetpack Race', 'JPR'),
            5:  ('Parachute Race', 'Chute Race'),
            6:  ('Rope Race', 'RR'),
            7:  ('Big Rope Race', 'Big RR', 'BRR'),
            8:  ('Time Trial Rope Race', 'TTRR'),
            9:  ('Super Sheep Race', 'Supersheep Race', 'SSR', 'Sheep Race'),
            10: ('Tower Rope Race', 'Tower Race', 'Tower'),
            11: ('Wascar',),
            12: ('Shopper', 'Shopping', 'Rope Shopper', 'SHOPPA', 'HBisTheRealClod'),
            13: ('Bungee Shopper',),
            14: ('Chamber Shopper', 'Chamber'),
            15: ('Fly Shopper', 'Fly'),
            16: ('Mole Shopper', 'Mole'),
            17: ('Pod Shopper', 'Pod'),
            18: ('Surf Shopper', 'Surf'),
            19: ('WxW Shopper', 'WxW', 'Wall to Wall', 'W2W', 'W3W', 'W4W'),
            20: ('Power Prodder',),
            21: ('Black Hole BnG', 'Rubber BnG'),
            # 22 ?
            23: ('Bow and Arrows', 'Bow & Arrow', 'Bow and Arrow', 'BnA', 'Bow&Arrow', 'B&A', 'Bow'),
            24: ('Big Bow and Arrow', 'Large Bow and Arrow', 'Big BnA', 'Large BnA', 'Worms Pinball', 'Pinball',
                 'Big Bow', 'BBnA'),
            25: ('Mine Madness',),
            26: ('Capture the Flag', 'CTF'),
            27: ('Fort', 'Forts'),
            28: ('Golf', 'Worms Golf'),
            29: ('Plop War', 'Plop'),
            30: ('Roper',),
            31: ('Sheep Fort',),
            32: ('Walk for Weapons', 'WFW'),
            33: ('Warmer', 'Warm'),
            34: ('Holy War', 'Holy'),
            35: ('Burning Girders',),
            36: ('Ghost Knocking', 'Ghost'),
            37: ('Darts',),
            38: ('BnG', 'B&G', 'Bazooka and Grenade', 'Bazookas and Grenades'),
            39: ('Elite',),
            40: ('Team17', 'T17'),
            41: ('Hysteria', 'Hyst'),
            42: ('Dabble and Fidget', 'Dabble & Fidget'),
            43: ('Supersheeper',),
            44: ('Aerial Classic', 'Aerial'),
            45: ('Abnormal', 'Ab'),
            46: ('Beginner',),
            47: ('Intermediate', 'Normal', 'Norm'),
            48: ('Pro',),
            49: ('Artillery',),
            50: ('Classic',),
            51: ('Armageddon',),
            52: ('Darkside', 'The Darkside'),
            53: ('NetBlitz',),
            54: ('Retro',),
            55: ('Strategic',),
            56: ('Sudden Sinking',),
            57: ('Tournament',),
            58: ('Blast Zone', 'WW3', 'World War 3'),
            59: ('Full Wormage', 'The Full Wormage', 'FW'),
            60: ('Testing', 'Test'),
            61: ('Solid Testing',),
            62: ('Tube Trap', 'Tube', 'TT'),
            63: ('Kaos Normal', 'Kaos'),
            64: ('Kaos Pro',),
            65: ('Aerial SD',),
            66: ('Neocombat',),
            67: ('Rubber Plop War',),
            68: ('Free Warmer', 'Freewarm'),
            69: ('Kaos Mole Shopper', 'Rubber Mole Shopper', 'Kaos Mole', 'Rubber Mole'),
            70: ('Only Crates', 'OnC'),
            71: ('Rowy',)
        }
        self.SCHEME_ID_MAP = dict(
            (scheme_name.upper(), scheme_id)
            for scheme_id, scheme_names in self.SCHEME_IDS_NAMES.items()
            for scheme_name in scheme_names
        )
        self.SCHEMES_FORMATTED = []
        scheme_bullet = '\N{SMALL BLUE DIAMOND}'
        scheme_alias_sep = '\N{BOX DRAWINGS LIGHT VERTICAL}'
        for scheme_names in self.SCHEME_IDS_NAMES.values():
            scheme_line = f'{scheme_bullet} {scheme_names[0]}'
            if len(scheme_names) > 1:
                scheme_line += f'  ( {f" {scheme_alias_sep} ".join(name for name in scheme_names[1:])} )'
            self.SCHEMES_FORMATTED.append(scheme_line)
        self.SCHEMES_FORMATTED = '\n'.join(sorted(self.SCHEMES_FORMATTED, key=lambda line: line.upper()))

        self.SNOOP_XSRF = '01557D3805'

        self.host_user_command_timeout = set()
        self.host_global_command_timeout = False

        self.wormnat_user_command_timeout = set()
        self.wormnat_global_command_timeout = False

        self.logger = logging.getLogger('WA_Logger')
        self.http_redir_url = WA_Settings.WA_Discord.get('http_redir_url')
        self.embed_color = WA_Settings.WA_Discord.get('embed_color')
        self.embed_icon = WA_Settings.WA_Discord.get('embed_icon')

    async def clear_wormnat_user_activity(self, user, delay=0.0):
        if delay:
            await asyncio.sleep(delay)
        self.wormnat_user_command_timeout.discard(user)

    async def clear_wormnat_global_activity(self, delay=0.0):
        if delay:
            await asyncio.sleep(delay)
        self.wormnat_global_command_timeout = False

    async def clear_host_user_activity(self, user, delay=0.0):
        if delay:
            await asyncio.sleep(delay)
        self.host_user_command_timeout.discard(user)

    async def clear_host_global_activity(self, delay=0.0):
        if delay:
            await asyncio.sleep(delay)
        self.host_global_command_timeout = False

    async def request_websnoop_host(self, name: str, scheme_id: int, password: str, channel: str):
        host_data = {
            'name':     name,
            'scheme':   str(scheme_id),
            'password': password,
            'channel':  channel,
            'xsrf':     self.SNOOP_XSRF
        }
        async with aiohttp.ClientSession() as session:
            with aiohttp.MultipartWriter('form-data') as mp_writer:
                for key, value in host_data.items():
                    part = mp_writer.append(value)
                    part.set_content_disposition('form-data', name=key)

                async with session.post(f'https://snoop.wormnet.net/data/host', data=mp_writer) as response:
                    return await response.text()


wa_commands = WA_Commands()

@discord.app_commands.command(description='Host a game from Discord via WebSnoop')
@discord.app_commands.describe(
    game_name='Choose a name that the game will be hosted as (defaults to "{scheme} for {name}")',
    scheme='Choose a scheme to host, use /schemes to get a list',
    password='An optional password to lock the game with')
async def host(interaction: discord.Interaction, scheme: str, game_name: str = '', password: str = ''):
    wa_commands.logger.warning(f' * Host command used by "{interaction.user.display_name}"'
                               f' ({interaction.user.id}) on Discord server'
                               f' "{interaction.guild.name}" on channel "#{interaction.channel.name}".'
                               f' {scheme=} | {game_name=} | {password=}')

    if not (scheme_id := wa_commands.SCHEME_ID_MAP.get(scheme.upper())):
        return await interaction.response.send_message(f'Scheme input not recognized: "{scheme}"', ephemeral=True)

    # forward_channel = interaction.client.settings[interaction.guild_id]['channels'][interaction.channel_id]['forward']
    forward_channel = 'anythinggoes'  # hardcode anythinggoes for now, to allow the command to work from anywhere
    channel_settings = interaction.client.settings[interaction.guild_id]['wormnet_channel_settings'][forward_channel]
    if 'Tf' in channel_settings:
        return await interaction.response.send_message(
            f'Cannot host in <#{interaction.channel_id}> as it forwards to WormNET'
            f' {discord.utils.escape_markdown("#" + forward_channel)} which does not allow hosting.')

    if game_name:
        has_bad_characters = False
        formatted_bad_characters_name = ''
        for char in game_name:
            if char in WA1252.decoding_table:
                formatted_bad_characters_name += discord.utils.escape_markdown(char)
            else:
                has_bad_characters = True
                formatted_bad_characters_name += f'**__{discord.utils.escape_markdown(char)}__**'
            formatted_bad_characters_name += '\N{Zero Width Space}'  # to allow discord formatting to be side by side

        if has_bad_characters:
            return await interaction.response.send_message(
                "**Unable to host. Please choose another game name.**\n"
                "One or more characters in your chosen game name cannot be represented with WA's character set.\n"
                f'To avoid this error change any bold underlined characters in your game name:\n'
                f'> {formatted_bad_characters_name}\n\n'
                'Allowed characters reference: <https://worms2d.info/WA_character_table>',
                ephemeral=True)

    if wa_commands.host_global_command_timeout:
        return await interaction.response.send_message('This command has been used too recently', ephemeral=True)

    if interaction.user.id in wa_commands.host_user_command_timeout:
        return await interaction.response.send_message('You have used this command too recently', ephemeral=True)

    if not game_name:
        unaliased_scheme_name = wa_commands.SCHEME_IDS_NAMES[scheme_id][0]
        if all(char in WA1252.decoding_table for char in interaction.user.display_name):
            game_name = f'{unaliased_scheme_name} for {interaction.user.display_name}'
        else:
            game_name = unaliased_scheme_name

    wa_commands.host_user_command_timeout.add(interaction.user.id)
    wa_commands.host_global_command_timeout = True
    host_response = json.loads(await wa_commands.request_websnoop_host(game_name, scheme_id, password, forward_channel))
    asyncio.create_task(wa_commands.clear_host_global_activity(10))
    asyncio.create_task(wa_commands.clear_host_user_activity(interaction.user.id, 20))

    if error := host_response['host']['error']:
        return await interaction.response.send_message(f'WebSnoop returned error:\n> {error}', ephemeral=True)

    return await interaction.response.send_message(
        'Your game is hosted, WebSnoop will advertise it once you join.\n'
        f'Click this link to join your game: <{host_response["host"]["url"]}>',
        ephemeral=True)


@discord.app_commands.command(description='Get a list of schemes supported by /host')
async def schemes(interaction: discord.Interaction):
    wa_commands.logger.warning(f' * Schemes command used by "{interaction.user.display_name}"'
                               f' ({interaction.user.id}) on Discord server'
                               f' "{interaction.guild.name}" on channel "#{interaction.channel.name}"')

    return await interaction.response.send_message(
        'Websnoop schemes list (aliases in brackets):\n'
        f'{wa_commands.SCHEMES_FORMATTED}',
        ephemeral=True)


@discord.app_commands.command(description='Post the wormNAT2 installation TL;DR guide.')
async def wormnat_guide(interaction: discord.Interaction):
    wa_commands.logger.warning(f' * Wormnat guide command used by "{interaction.user.display_name}"'
                               f' ({interaction.user.id}) on Discord server'
                               f' "{interaction.guild.name}" on channel "#{interaction.channel.name}"')

    if wa_commands.wormnat_global_command_timeout:
        return await interaction.response.send_message('This command has been used too recently', ephemeral=True)

    if interaction.user.id in wa_commands.wormnat_user_command_timeout:
        return await interaction.response.send_message('You have used this command too recently', ephemeral=True)

    forward_channels = interaction.client.settings[interaction.guild_id]['channels']
    if interaction.channel_id not in forward_channels or forward_channels[interaction.channel_id]['forward'] != 'help':
        return await interaction.response.send_message(
            'This command can only be used in a channel that forwards to WormNET #help',
            ephemeral=True)

    wa_commands.wormnat_user_command_timeout.add(interaction.user.id)
    wa_commands.wormnat_global_command_timeout = True
    asyncio.create_task(post_wormnat_guide())
    asyncio.create_task(wa_commands.clear_wormnat_global_activity(10))
    asyncio.create_task(wa_commands.clear_wormnat_user_activity(interaction.user.id, 20))

    return await interaction.response.send_message('WormNAT2 TL;DR Guide post request sent.', ephemeral=True)
