#!/usr/bin/env python3

import asyncio
import logging
import traceback
from datetime import datetime, timezone, timedelta

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
    if message.command == 'QUIT':
        channel = 'help'
    else:
        channel = message.parameters[0][1:].lower()

    # only write join / part messages if user has written in #help
    if sender in irc.activity[channel]:
        # if not parting/quitting or written in a while, remove user from activity list
        time_since_activity = datetime.now(timezone.utc) - irc.activity[channel][sender]
        if message.command not in ('PART', 'QUIT') and time_since_activity > timedelta(minutes=5):
            return irc.activity[channel].pop(sender, None)

        # if parting/quitting, always show, and remove from activity list if quitting
        if message.command == 'QUIT':
            irc.activity[channel].pop(sender, None)
            message = f'{sender} has {message.command.lower()} WormNET! [{message.parameters}]'
        else:
            message = f'{sender} has {message.command.lower()}ed the channel!'
        return await discord.send_message(irc_channel=channel, sender=sender, message=message, action=True)


# MAIN #
try:
    # LOGGING SETUP #
    logger = logging.getLogger('WA_Logger')
    logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    # ASYNCIO SETUP #
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
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
    irc.handlers['help']['QUIT'] = irc_entry_help_handler
    # irc.handlers['anythinggoes']['PRIVMSG'] = irc.default_privmsg_handler

    loop.run_forever()  # this works, NICE!
except KeyboardInterrupt:
    logger.critical(' ! Encountered KbdInterrupt. Shutting down.\n')
    loop.stop()
except Exception as e:
    print(e)
