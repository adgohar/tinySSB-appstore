import sys
import json
import os
from pure25519 import SigningKey, VerifyingKey, create_keypair, open as open25519
from simplepub import bipf, replica
from simplepub.bipf import _dec_list

def verify_fct(fid, signature, message):
    print(f"Verifying {signature} {message}")
    return (open25519(signature + message, fid) != None)  #wichtig

def updateCuratorFeed():

    curatorfid = None
    
    for folder in os.listdir("CuratorFeed"):
        fid = bytes.fromhex(folder)
        r = replica.Replica("./CuratorFeed", fid, verify_fct)
        try:
            firstEntry = r.read(1)
        except:
            firstEntry = None
        if firstEntry:
            decodedFirstEntry, _ = bipf.decode(firstEntry)
            decodedElements = []

            for element in decodedFirstEntry:
                decodedElement, _ = bipf.decode(element)
                decodedElements.append(decodedElement)

            firstElementStr = decodedElements[0]

            if firstElementStr == "CuratorFeed":
                curatorfid = fid
                break
            else:
                pass
    if curatorfid is None:
        createCuratorFeed()

    file_path = "curator.json"
    data = {}

    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            try:
                data = json.load(file)
            except json.JSONDecodeError:
                data = {}

    curatorfid = data.get("fid")
    curatorSignKey = data.get(curatorfid)


    devCuratorFeeds = []

    #open the Developer Feeds directory
    for folder in os.listdir("DeveloperFeeds"):
        fid = bytes.fromhex(folder)
        r = replica.Replica("./DeveloperFeeds", fid, verify_fct)
        try:
            firstEntry = r.read(1)
        except:
            firstEntry = None
        if firstEntry:
            decodedFirstEntry, _ = bipf.decode(firstEntry)
            decodedElements = []

            for element in decodedFirstEntry:
                decodedElement, _ = bipf.decode(element)
                decodedElements.append(decodedElement)

            firstElementStr = decodedElements[0]

            if firstElementStr == "DevCuratorFeed":
                devCuratorFeeds.append(fid.hex())
            else:
                pass

    print(f"Dev Curator Feeds {devCuratorFeeds}")
    
    for curatorFeed in devCuratorFeeds:
        #get list of apps in the curator feed
        appList = showDeveloperList(curatorFeed)
        for app in appList:
            #check if the app is already in the curator feed
            if isInCuratorFeed(app) is not None:
                print(f"{app[2]} is already in Curator Feed (unchanged)")
                continue

            r_curator = replica.Replica("./CuratorFeed", bytes.fromhex(curatorfid), verify_fct)
            curatorList = [
                bipf.dumps("DevApp"),
                bipf.dumps(app[1]),
                bipf.dumps(app[2]),
                bipf.dumps(app[3]),
                bipf.dumps(app[4]),
                bipf.dumps(app[5]),
                bipf.dumps(app[6])
            ]
            encodedCuratorList = bipf.dumps(curatorList)
            if r_curator is not None:
                print(f"Writing {app[2]} to Curator Feed")
                r_curator.write_new(encodedCuratorList, SigningKey(bytes.fromhex(curatorSignKey)))
            else:
                pass

def showDeveloperFeeds():
    #loop through all folders in the DeveloperFeeds directory and return the feeds
    devCuratorFeeds = []

    for folder in os.listdir("DeveloperFeeds"):
        fid = bytes.fromhex(folder)
        r = replica.Replica("./DeveloperFeeds", fid, verify_fct)
        try:
            firstEntry = r.read(1)
        except:
            firstEntry = None
        if firstEntry:
            decodedFirstEntry, _ = bipf.decode(firstEntry)
            decodedElements = []

            for element in decodedFirstEntry:
                decodedElement, _ = bipf.decode(element)
                decodedElements.append(decodedElement)

            firstElementStr = decodedElements[0]

            if firstElementStr == "DevCuratorFeed":
                devCuratorFeeds.append(fid.hex())
            else:
                pass
    return devCuratorFeeds


def showCuratorFeed():
    #loop through all folders in the DeveloperFeeds directory and return the feeds
    devCuratorFeeds = []

    for folder in os.listdir("CuratorFeed"):
        fid = bytes.fromhex(folder)
        r = replica.Replica("./CuratorFeed", fid, verify_fct)
        try:
            firstEntry = r.read(1)
        except:
            firstEntry = None
        if firstEntry:
            decodedFirstEntry, _ = bipf.decode(firstEntry)
            decodedElements = []

            for element in decodedFirstEntry:
                decodedElement, _ = bipf.decode(element)
                decodedElements.append(decodedElement)

            firstElementStr = decodedElements[0]

            if firstElementStr == "DevCuratorFeed":
                devCuratorFeeds.append(fid.hex())
            else:
                pass
    return devCuratorFeeds

def showDeveloperList(curatorfid: str = None):
    #loop through all apps and return them as a list

    if curatorfid is None:        
        #get the curator feed from the devCurator.json file
        file_path = "curator.json"
        data = {}

        if os.path.exists(file_path):
            with open(file_path, "r") as file:
                try:
                    data = json.load(file)
                except json.JSONDecodeError:
                    data = {}

        curatorfid = data.get("fid")

    curatorFidBytes = bytes.fromhex(curatorfid)
    r = replica.Replica("./DeveloperFeeds", curatorFidBytes, verify_fct)
    lastSeq = r.state['max_seq']

    appList = []
    appListNames = []

    for i in range(lastSeq, 0, -1):
        entry = r.read(i)
        decodedEntry, _ = bipf.decode(entry)
        decodedElements = []

        for element in decodedEntry:
            decodedElement, _ = bipf.decode(element)
            decodedElements.append(decodedElement)

        firstElementStr = decodedElements[0]

        if firstElementStr == "DevApp":
            appFeedID = decodedElements[1]
            appName = decodedElements[2]
            appDesc = decodedElements[3]
            developerID = decodedElements[4]
            status = decodedElements[5]
            details = decodedElements[6]
            #make sure the app is not already in the list using appName
            if appName not in appListNames:
                appListNames.append(appName)
                appList.append(decodedElements)
        else:
            pass
    return appList

def showCuratorList(curatorfid: str = None):
    #loop through all apps and return them as a list

    if curatorfid is None:        
        #get the curator feed from the devCurator.json file
        file_path = "curator.json"
        data = {}

        if os.path.exists(file_path):
            with open(file_path, "r") as file:
                try:
                    data = json.load(file)
                except json.JSONDecodeError:
                    data = {}

        curatorfid = data.get("fid")

    curatorFidBytes = bytes.fromhex(curatorfid)
    r = replica.Replica("./CuratorFeed", curatorFidBytes, verify_fct)
    lastSeq = r.state['max_seq']

    appList = []
    appListNames = []

    for i in range(lastSeq, 0, -1):
        entry = r.read(i)
        decodedEntry, _ = bipf.decode(entry)
        decodedElements = []

        for element in decodedEntry:
            decodedElement, _ = bipf.decode(element)
            decodedElements.append(decodedElement)

        firstElementStr = decodedElements[0]

        if firstElementStr == "DevApp":
            appFeedID = decodedElements[1]
            appName = decodedElements[2]
            appDesc = decodedElements[3]
            developerID = decodedElements[4]
            status = decodedElements[5]
            details = decodedElements[6]
            #make sure the app is not already in the list using appName
            if appName not in appListNames:
                appListNames.append(appName)
                appList.append(decodedElements)
        else:
            pass
    return appList

def readFromCuratorFeed(fid, seq):
    #read from the curator feed
    #return the app details
    #if the app is not in the curator feed, return None

    r = replica.Replica("./CuratorFeed", fid, verify_fct)
    entry = r.read(seq)
    decodedEntry, _ = bipf.decode(entry)
    decodedElements = []

    for element in decodedEntry:
        decodedElement, _ = bipf.decode(element)
        decodedElements.append(decodedElement)

    return decodedElements



def isInCuratorFeed(app):
    #check if the app is in the curator feed
    #if it is, return the app details
    #if not, return None

    #get the curator feed from the curator.json file
    file_path = "curator.json"
    data = {}

    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            try:
                data = json.load(file)
            except json.JSONDecodeError:
                data = {}

    curatorfid = data.get("fid")

    curatorFidBytes = bytes.fromhex(curatorfid)
    r = replica.Replica("./CuratorFeed", curatorFidBytes, verify_fct)
    lastSeq = r.state['max_seq']

    for i in range(lastSeq, 0, -1):
        entry = r.read(i)
        decodedEntry, _ = bipf.decode(entry)
        decodedElements = []

        for element in decodedEntry:
            decodedElement, _ = bipf.decode(element)
            decodedElements.append(decodedElement)

        firstElementStr = decodedElements[0]

        if firstElementStr == "DevApp":
            if decodedElements == app:
                return 1
            else:
                pass
        else:
            pass
    return None

def getCuratorFeed():
    #get the curator feed from the curator.json file
    file_path = "curator.json"
    data = {}

    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            try:
                data = json.load(file)
            except json.JSONDecodeError:
                data = {}

    curatorfid = data.get("fid")

    return curatorfid


def createCuratorFeed():

    keypair = create_keypair()
    signingKey = keypair[0]
    verifyKey = keypair[1]
    fid = verifyKey.vk_s

    #check if a keypaid exists in curator.json
    file_path = "curator.json"
    data = {}

    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            try:
                data = json.load(file)
            except json.JSONDecodeError:
                data = {}
    
    if data.get("fid") is not None:
        fid = bytes.fromhex(data.get("fid"))
        signingKey = SigningKey(bytes.fromhex(data.get(fid.hex())))
        verifyKey = VerifyingKey(bytes.fromhex(fid.hex()))

    print(f"SIGNING KEY {signingKey.sk_s.hex()}")
    print(f"VERIFY KEY {verifyKey.vk_s.hex()}")
    
    r = replica.Replica("./CuratorFeed", fid, verify_fct)
    r.state['max_seq'] = 0
    print(r.state['max_seq'])
    print(f"New Replica Created {fid.hex()}")
    
    # Create the list to be encoded
    curatorList = [
        bipf.dumps("CuratorFeed"),
        bipf.dumps(fid),
    ]

    file_path = "curator.json"
    data = {}

    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            try:
                data = json.load(file)
            except json.JSONDecodeError:
                data = {}

    data["fid"] = fid.hex()
    data[fid.hex()] = signingKey.sk_s.hex()

    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)

    # Encode the list of encoded elements
    encodedCuratorList = bipf.dumps(curatorList)
    
    if encodedCuratorList is not None:
        print(f"ENCODED LIST BIPF {encodedCuratorList.hex()}")
    
    lastSeq = r.state['max_seq']
    if encodedCuratorList is not None:
        if r is not None:            
            attempt = r.write_new(encodedCuratorList, signingKey)
            print(f"Attempt {attempt}")

if __name__ == "__main__":
    updateCuratorFeed()
    sys.exit()