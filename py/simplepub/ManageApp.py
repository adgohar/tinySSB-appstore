import developer as dev
import developerCurator as devCurator
import sys

if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument('-command', choices=['commit', 'download', 'showReleases', 'setActiveRelease', 'getActiveRelease', 'end', 'status', 'update', 'generateCurator', 'showCuratorList'], required=True,
                    help='Command to execute')
    ap.add_argument('-path', type=str,
                    help='Path to the app folder')
    ap.add_argument('-version', type=str,
                    help='Version of the app')
    ap.add_argument('-comment', type=str,
                    help='Comment for the commit')
    ap.add_argument('-name', type=str,
                    help='Name of the app')
    
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
    elif args.command == "update":
        if args.name == None:
            print("Missing argument: name")
            sys.exit()
        #ask for category they want to update
        category = input("Enter the number of the category you would like to update: ")
        print("1. Description")
        print("2. Category")
        print("3. Age Rating")
        print("4. Rating")

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
        else:
            print("Invalid category number")
            sys.exit()
    elif args.command == "showCuratorList":
        curatorList = devCurator.showCuratorList()
        for curator in curatorList:
            print(curator)


        