#!/usr/bin/env python3

import asyncio
import logging
import traceback
from datetime import datetime, timezone

from wa_discord import WA_Discord
from wa_gamelist import WA_Gamelist
from wa_irc import WA_IRC
from wa_settings import WA_Settings

# FUNCTIONS #

def fatal_handler(loop, context):
    exception = context.get('exception')
    logger.critical(f' ! {exception}')
    logger.critical(' ! Encountered FATAL error. Shutting down.\n')
    traceback.print_exception(type(exception), exception, exception.__traceback__)
    loop.stop()


async def irc_entry_help_handler(connection, message):
    sender = message.prefix.nick
    channel = message.parameters[0][1:].lower()

    # only write join / part messages if user has written in #help
    if sender in irc.activity[channel]:
        # if parting, always show, otherwise only if written in the last 5 minutes
        if (datetime.now(timezone.utc) - irc.activity[channel][sender]).total_seconds() <= 5 * 60 or message.command == 'PART':
            message = f'{sender} has {message.command.lower()}ed the channel!'
            return await discord.send_message(irc_channel=channel, sender=sender, message=message, action=True)
        # if not parting or have not written in a while, remove user from activity list
        else:
            return irc.activity[channel].pop(sender, None)


# MAIN #
try:
    # LOGGING SETUP #
    logger = logging.getLogger('WA_Logger')
    logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    # ASYNCIO SETUP #
    loop = asyncio.get_event_loop()
    loop.set_exception_handler(fatal_handler)

    # IRC SETUP #
    irc = WA_IRC(loop=loop, **WA_Settings.WA_IRC)
    loop.create_task(irc.connect())

    # DISCORD SETUP #
    discord = WA_Discord(**WA_Settings.WA_Discord)
    loop.create_task(discord.update_userlists(irc.channels, interval=7))
    loop.create_task(discord.run())

    # LIST SETUP #
    gamelist = WA_Gamelist(**WA_Settings.WA_Gamelist)
    loop.create_task(gamelist.update(discord))

    # FINAL SETUP #
    discord.forward_message = irc.send_message
    irc.forward_message = discord.send_message
    irc.commands['help'] = True
    irc.commands['anythinggoes'] = False
    irc.handlers['help']['PRIVMSG'] = irc.default_privmsg_handler
    irc.handlers['help']['JOIN'] = irc_entry_help_handler
    irc.handlers['help']['PART'] = irc_entry_help_handler
    irc.handlers['anythinggoes']['PRIVMSG'] = irc.default_privmsg_handler

    loop.run_forever()  # this works, NICE!
except Exception as e:
    print(e)
