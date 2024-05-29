import asyncio
import json
import os
import developer as dev
import developerCurator as devCurator
import devpub as devpub
import sys


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument('-command', choices=['commit', 'download', 'showReleases', 'setActiveRelease', 'getActiveRelease', 'end', 'status', 'updateCurator', 'generateCurator', 'showCuratorList', 'sendCurator', 'receiveCurator'], required=True,
                    help='Command to execute')
    ap.add_argument('-path', type=str,
                    help='Path to the app folder')
    ap.add_argument('-version', type=str,
                    help='Version of the app')
    ap.add_argument('-comment', type=str,
                    help='Comment for the commit')
    ap.add_argument('-name', type=str,
                    help='Name of the app')
    ap.add_argument('-data', type=str, default='./data', metavar='DATAPATH',
                    help='path to persistency directory (default: ./data)')
    ap.add_argument('senduri', type=str, nargs='?',
                    default='ws://127.0.0.1:8081',
                    help='TCP port if responder, URI if intiator (default is ws://127.0.0.1:8081)')
    ap.add_argument('receiveuri', type=str, nargs='?',
                    default='ws://127.0.0.1:8080',
                    help='TCP port if responder, URI if intiator (default is ws://127.0.0.1:8080)')
    args = ap.parse_args()

    if args.command == None:
        print("Missing command")
        sys.exit()

    if args.command == "commit":
        if args.path == None or args.version == None or args.comment == None or args.name == None:
            print("Missing arguments: path, version, comment or name")
            sys.exit()
        dev.commitApp(args.name, args.path, args.version, args.comment)
    elif args.command == "download":
        if args.name == None or args.path == None:
            print("Missing arguments: name or path")
            sys.exit()
        dev.downloadApp(args.name, args.path, args.version)
    elif args.command == "showReleases":
        if args.name == None:
            print("Missing argument: name")
            sys.exit()
        releases = dev.showReleases(args.name)
        for release in releases:
            print(release)
    elif args.command == "setActiveRelease":
        if args.name == None or args.version == None:
            print("Missing arguments: name or version")
            sys.exit()
        dev.setActiveRelease(args.name, args.version)
    elif args.command == "getActiveRelease":
        if args.name == None:
            print("Missing argument: name")
            sys.exit()
        print(dev.getActiveRelease(args.name))
    elif args.command == "end":
        if args.name == None:
            print("Missing argument: name")
            sys.exit()
        if args.comment == None:
            dev.endApp(args.name)
            devCurator.updateAppStatus(args.name, "Ended")
        else:
            dev.endApp(args.name, args.comment)
            devCurator.updateAppStatus(args.name, "Ended")
    elif args.command == "status":
        if args.name == None:
            print("Missing argument: name")
            sys.exit()
        print(dev.getAppStatus(args.name))
    elif args.command == "generateCurator":
        devCurator.generateCuratorFeed()
    elif args.command == "updateCurator":
        if args.name == None:
            print("Missing argument: name")
            sys.exit()
        #ask for category they want to update
        print("1. Description")
        print("2. Category")
        print("3. Age Rating")
        print("4. Rating")
        print("5. Size")
        print("6. Url")
        category = input("Enter the number of the category you would like to update: ")
        

        if category == "1":
            #ask for new description
            description = input("Enter the new description: ")
            devCurator.updateDescription(args.name, description)
        elif category == "2":
            #ask for new category
            category = input("Enter the new category: ")
            devCurator.updateCategory(args.name, category)
        elif category == "3":
            #ask for new age rating
            ageRating = input("Enter the new age rating: ")
            devCurator.updateAgeRating(args.name, ageRating)
        elif category == "4":
            #ask for new rating
            rating = input("Enter the new rating: ")
            devCurator.updateRating(args.name, rating)
        elif category == "5":
            #ask for new Size
            size = input("Enter the new size: ")
            devCurator.updateSize(args.name, size)
        elif category == "6":
            #ask for new url
            url_input = input("Enter the new url(s) (seperate by a comma if multiple URLs): ")
            urls = [url.strip() for url in url_input.split(',')]  # Split the input string by commas and strip any extra whitespace
            devCurator.updateUrl(args.name, urls)
        else:
            print("Invalid category number")
            sys.exit()
    elif args.command == "showCuratorList":
        curatorList = devCurator.showCuratorList()
        for curator in curatorList:
            print(curator)
    elif args.command == "sendCurator":
        if args.senduri == None or args.data == None:
            print("Missing argument: senduri or data")
            sys.exit()
        else:
            #get the curator feed from the devCurator.json file
            file_path = "devCurator.json"
            data = {}

            if os.path.exists(file_path):
                with open(file_path, "r") as file:
                    try:
                        data = json.load(file)
                    except json.JSONDecodeError:
                        data = {}

            curatorfid = data.get("fid")

            curatorFidBytes = bytes.fromhex(curatorfid)

            asyncio.run(devpub.main(args.data, curatorFidBytes, args.senduri))

    elif args.command == "receiveCurator":
        if args.receiveuri == None or args.data == None:
            print("Missing argument: receiveuri or data")
            sys.exit()
        else:
            asyncio.run(devpub.receiveCurator(args.data, args.receiveuri))