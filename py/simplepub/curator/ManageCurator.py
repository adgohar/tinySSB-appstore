import asyncio
import json
import os
import curpub as cp
import Curator as cur
import spub as sp
import sys

if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument('-command', choices=['startServers', 'startSendServer', 'startReceiveServer', 'updateCuratorFeed', 'showDeveloperFeeds', 'showCuratorList', 'updateCurator'], required=True,
                    help='Command to execute')
    ap.add_argument('-developerdata', type=str, default='DeveloperFeeds', metavar='DATAPATH',
                    help='path to persistency directory (default: /DeveloperFeeds)')
    ap.add_argument('-curatordata', type=str, default='CuratorFeed', metavar='DATAPATH',
                    help='path to persistency directory (default: /CuratorFeed)')
    ap.add_argument('senduri', type=int, nargs='?',
                    default='8080',
                    help='TCP port if responder, URI if intiator (default is 8080)')
    ap.add_argument('-name', type=str,
                    help='Name of the app')
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
        args.data = args.developerdata
        args.role = 'in'
        args.v = False
        args.uri_or_port = args.receiveuri
        args.ble = False
        gosetKey = bytes.fromhex('0000000000000000000000000000000000000000000000000000000000000000')
        asyncio.run(cp.mainIn(args.data ,args.uri_or_port, gosetKey))
        sys.exit()

    elif args.command == "updateCuratorFeed":
        cur.updateCuratorFeed()
        sys.exit()

    elif args.command == "updateCurator":
        if args.name == None:
            print("Missing argument: name")
            sys.exit()
        #ask for category they want to update
        print("1. Category")
        print("2. Age Rating")
        print("3. Rating")
        print("4. Size")
        print("5. Url")
        category = input("Enter the number of the category you would like to update: ")
        
        if category == "1":
            #ask for new category
            category = input("Enter the new category: ")
            cur.updateCategory(args.name, category)
        elif category == "2":
            #ask for new age rating
            ageRating = input("Enter the new age rating: ")
            cur.updateAgeRating(args.name, ageRating)
        elif category == "3":
            #ask for new rating
            rating = input("Enter the new rating: ")
            cur.updateRating(args.name, rating)
        elif category == "4":
            #ask for new Size
            size = input("Enter the new size: ")
            cur.updateSize(args.name, size)
        elif category == "5":
            #ask for new url
            url_input = input("Enter the new url(s) (seperate by a comma if multiple URLs): ")
            urls = [url.strip() for url in url_input.split(',')]  # Split the input string by commas and strip any extra whitespace
            cur.updateUrl(args.name, urls)
        else:
            print("Invalid category number")
            sys.exit()

    elif args.command == "showDeveloperFeeds":
        cur.showDeveloperFeeds()
        sys.exit()

    elif args.command == "showCuratorList":
        print(cur.showCuratorList())
        sys.exit()