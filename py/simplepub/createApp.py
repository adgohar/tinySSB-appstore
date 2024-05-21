import developer as dev
import sys



if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument('-name', type=str,
                    help='enable Bluetooth Low Energ (default: off)')
    ap.add_argument('-description', type=str, default='No Description',
                    help='Description of your app (default: No Description)')
    
    args = ap.parse_args()

    #Make sure the name is not empty
    if args.name == None:
        print("Name cannot be empty")
        sys.exit()

    #Check if the app already exists
    if dev.getFeedID(args.name):
        print("App with that name already exists")
        sys.exit()
    
    dev.createAppFeed(args.name, args.description)
    print("App created successfully")
    sys.exit()