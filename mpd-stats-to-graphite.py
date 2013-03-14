#!/usr/bin/env python
"""
MPD-to-Graphite stats collector daemon

This script collects some numbers ("stats" and "status" results) from an mpd
server and sends them to a graphite server. Sends stats every second.

By: pixelistik <code@pixelistik.de>

Originally based on http://jatreuman.indefero.net/p/python-mpd/page/ExampleStats/
"""
import sys
import time
import socket

from mpd import (MPDClient, CommandError)

#######################
MPD_HOST = ''
MPD_PORT = 6600
PASSWORD = False

GRAPHITE_HOST = ''
GRAPHITE_PORT = 2003
#######################

CON_ID = {'host':MPD_HOST, 'port':MPD_PORT}

def mpdConnect(client, con_id):
    """
    Simple wrapper to connect MPD.
    """
    try:
        client.connect(**con_id)
    except socket.error:
        return False
    return True

def send_value(key, value):
    """
    Send a value with current timestamp to graphite
    http://coreygoldberg.blogspot.de/2012/04/python-getting-data-into-graphite-code.html
    """
    message = 'multimedia.mpd.%s %s %d\n' % (key, value, int(time.time()))

    try:
        sock = socket.socket()
        sock.connect((GRAPHITE_HOST, GRAPHITE_PORT))
        sock.sendall(message)
        sock.close()
    except socket.error:
        return False

    return True

def main():
    client = MPDClient()

    while True:
        if not mpdConnect(client, CON_ID):
            sys.stderr.write('fail to connect MPD server.')
            sys.exit(1)

        results = dict(client.status().items() + client.stats().items())

        for key, value in results.items():
            if not send_value(key, value):
                sys.stderr.write('failed to send value to graphite.')
                sys.exit(1)

        client.disconnect()
        time.sleep(1)

if __name__ == "__main__":
    main()

