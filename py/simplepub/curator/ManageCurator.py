import asyncio
import json
import os
import curpub as cp
import Curator as cur
import sys

if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument('-command', choices=['startServers', 'startSendServer', 'startReceiveServer', 'updateCuratorFeed', 'showDeveloperFeeds', 'showCuratorList'], required=True,
                    help='Command to execute')
    ap.add_argument('-developerdata', type=str, default='DeveloperFeeds', metavar='DATAPATH',
                    help='path to persistency directory (default: /DeveloperFeeds)')
    ap.add_argument('-curatordata', type=str, default='CuratorFeed', metavar='DATAPATH',
                    help='path to persistency directory (default: /CuratorFeed)')
    ap.add_argument('senduri', type=int, nargs='?',
                    default='8080',
                    help='TCP port if responder, URI if intiator (default is 8080)')
    ap.add_argument('receiveuri', type=int, nargs='?',
                    default='8081',
                    help='TCP port if responder, URI if intiator (default is 8081)')
    args = ap.parse_args()

    if args.command == None:
        print("Missing command")
        sys.exit()

    elif args.command == "startSendServer":
        asyncio.run(cp.mainOut(args.curatordata, args.senduri))
        sys.exit()

    elif args.command == "startReceiveServer":
        asyncio.run(cp.mainIn(args.developerdata, args.receiveuri))
        sys.exit()

    elif args.command == "updateCuratorFeed":
        cur.updateCuratorFeed()
        sys.exit()

    elif args.command == "showDeveloperFeeds":
        cur.showDeveloperFeeds()
        sys.exit()

    elif args.command == "showCuratorList":
        print(cur.showCuratorList())
        sys.exit()