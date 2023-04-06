#!/usr/bin/python3

import socket
from time import time
import asyncio


async def main():
    server = 'wormnet1.team17.com'
    port = 6667
    password = 'PHILCARLISLE'[::-1]
    channel = '#Help'
    nick = 'WormNAT2Guide'

    login_commands = (
        f'PASS {password}\r\n'
        f'NICK {nick}\r\n'
        f'USER Username hostname servername :0 13 GB Armabuddy WormNAT2 TL;DR guide poster\r\n'  # 13 = snooper rank
    ).encode('wa1252')

    wait_secs = 5

    def pad(pad_amount):
        return '\N{NO-BREAK SPACE}' * pad_amount

    def epad(pad_amount):
        return pad(pad_amount) + ' '

    # comma at end = new msg with name prefix | no comma at end = string gets prepended to next string as 1 long message
    msgs = (
        f'{epad(110)}'
        f'1. Extract this into your W:A installation folder:{epad(55)}'
        f'{pad(6)}http://worms.thecybershadow.net/wormkit/wkWormNAT2.zip',
        f'{epad(110)}'
        f'2. Enable mods:{epad(106)}'
        f'{pad(6)}W:A main menu > Options > Advanced > Load wormkit modules',
        f'{epad(110)}'
        '3. Restart the game.',
        f'{epad(110)}'
        f'Hosting with the host button in #AnythingGoes should now allow people to join.{epad(4)}'
        'More info & other hosting methods here: https://worms2d.info/Hosting_Guide'
    )

    async def wait_for_response(desired_response):
        response = ''
        end_time = time() + wait_secs
        print('Waiting for:', desired_response)
        while True:
            try:
                response += irc_sock.recv(4096).decode('wa1252')
            except (socket.timeout, BlockingIOError):
                pass  # no data atm

            if desired_response in response:
                print('Found.')
                break
            if time() > end_time:
                print(f'Unable to get a response within {wait_secs} sec')
                print(f'==== response ====:\n{response}\n====')
                exit(1)
            await asyncio.sleep(0.5)

    irc_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    irc_sock.connect((server, port))
    irc_sock.setblocking(False)  # don't block code on recv

    irc_sock.send(login_commands)
    await wait_for_response(f':{server} 376 {nick} :End of /MOTD command.')

    irc_sock.send(f'JOIN {channel}\r\n'.encode('wa1252'))
    await wait_for_response(f':{server} 366 {nick} {channel} :End of /NAMES list.')

    await asyncio.sleep(2)

    out = ''.join(f'privmsg {channel} :{msg}\r\n' for msg in msgs).encode('wa1252')
    print(f'Sending combined msg.')
    irc_sock.send(out)

    await asyncio.sleep(1)

    print('Parting and quitting.')
    irc_sock.send(f'PART {channel}\r\n'.encode('wa1252'))
    irc_sock.send(b'QUIT\r\n')
    irc_sock.close()
    print('Done')


if __name__ == '__main__':
    main()
