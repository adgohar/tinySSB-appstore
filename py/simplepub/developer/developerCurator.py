import sys
import json
import os
from pure25519 import SigningKey, VerifyingKey, create_keypair
from simplepub import bipf, replica
from simplepub.bipf import _dec_list
import developer as dev

def generateCuratorFeed():
    #loop through all folders in the data directory and for each folder get the first entry
    #if the first entry does not have "AppDev" as the first element, create a new folder with a new app feed
    curatorfid = None
    
    for folder in os.listdir("data"):
        fid = bytes.fromhex(folder)
        r = replica.Replica("./data", fid, dev.verify_fct)
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
                curatorfid = fid
                break
            else:
                pass
    if curatorfid is None:
        createCuratorFeed()
        insertAppsIntoCuratorFeed()
    else:
        insertAppsIntoCuratorFeed()

def insertAppsIntoCuratorFeed():
    #loop through each app and insert it into the curator feed with the following format
    # [DevApp, AppFeedID, AppName, AppDesc, DeveloperID, Status, Details]
    # where developer id would be the curator feed id and details is an empty json string
    
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
    #get private key from the devCurator.json file
    curatorPrivateKey = data.get(curatorfid)
    
    curatorFidBytes = bytes.fromhex(curatorfid)
    r = replica.Replica("./data", curatorFidBytes, dev.verify_fct)

    appDevID = curatorFidBytes.hex()

    for folder in os.listdir("data"):
        fid = bytes.fromhex(folder)
        r_new = replica.Replica("./data", fid, dev.verify_fct)
        try:
            firstEntry = r_new.read(1)
        except:
            firstEntry = None
        if firstEntry:
            decodedFirstEntry, _ = bipf.decode(firstEntry)
            decodedElements = []

            for element in decodedFirstEntry:
                decodedElement, _ = bipf.decode(element)
                decodedElements.append(decodedElement)

            firstElementStr = decodedElements[0]

            if firstElementStr == "APP":
                appName = decodedElements[2]
                if getAppFromCurator(appName) is not None:
                    print(f"{appName} is already in Curator Feed")                    
                    continue
                appDesc = decodedElements[3]
                status = dev.getAppStatus(appName)
                details = "{}"
                curatorList = [
                    bipf.dumps("DevApp"),
                    bipf.dumps(fid),
                    bipf.dumps(appName),
                    bipf.dumps(appDesc),
                    bipf.dumps(appDevID),
                    bipf.dumps(status),
                    bipf.dumps(details)
                ]
                encodedCuratorList = bipf.dumps(curatorList)
                if encodedCuratorList is not None:
                    print(f"ENCODED LIST BIPF {encodedCuratorList.hex()}")
                lastSeq = r.state['max_seq']
                print(f"Last Seq {lastSeq}")
                if r is not None:
                    print(f"Writing to Curator Feed")
                    r.write_new(encodedCuratorList, SigningKey(bytes.fromhex(curatorPrivateKey)))
                else:
                    pass
            else:
                pass

def showCuratorList(curatorfid: str = None):
    #loop through all apps and return them as a list

    if curatorfid is None:        
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
    r = replica.Replica("./data", curatorFidBytes, dev.verify_fct)
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

def getAppFromCurator(appNameSearch: str, curatorfid: str = None):

    if curatorfid is None:

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

    r = replica.Replica("./data", bytes.fromhex(curatorfid), dev.verify_fct)
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
            appFeedID = decodedElements[1]
            appName = decodedElements[2]
            appDesc = decodedElements[3]
            developerID = decodedElements[4]
            status = decodedElements[5]
            details = decodedElements[6]
            if appName == appNameSearch:
                return decodedElements
            else:
                pass
        else:
            pass
    print("App not found")
    return None

def updateCategory(appNameSearch: str, newCategory: str):
    #get app details
    appDetails = getAppFromCurator(appNameSearch)[6]
    appDetailsJson = json.loads(appDetails)
    appDetailsJson["category"] = newCategory
    newAppDetails = json.dumps(appDetailsJson)
    updateAppDetails(appNameSearch, newAppDetails)

def updateAgeRating(appNameSearch: str, newAgeRating: str):
    #get app details
    appDetails = getAppFromCurator(appNameSearch)[6]
    appDetailsJson = json.loads(appDetails)
    appDetailsJson["age"] = newAgeRating
    newAppDetails = json.dumps(appDetailsJson)
    updateAppDetails(appNameSearch, newAppDetails)

def updateRating(appNameSearch: str, newRating: str):
    #get app details
    appDetails = getAppFromCurator(appNameSearch)[6]
    appDetailsJson = json.loads(appDetails)
    appDetailsJson["rating"] = newRating
    newAppDetails = json.dumps(appDetailsJson)
    updateAppDetails(appNameSearch, newAppDetails)

def updateAppDetails(appNameSearch: str, newDetails: str):
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
    #get private key from the devCurator.json file
    curatorPrivateKey = data.get(curatorfid)
    
    curatorFidBytes = bytes.fromhex(curatorfid)

    appDevID = curatorFidBytes.hex()

    r = replica.Replica("./data", curatorFidBytes, dev.verify_fct)
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
            appFeedID = decodedElements[1]
            appName = decodedElements[2]
            appDesc = decodedElements[3]
            developerID = decodedElements[4]
            status = decodedElements[5]
            details = decodedElements[6]
            if appName == appNameSearch:
                curatorList = [
                    bipf.dumps("DevApp"),
                    bipf.dumps(appFeedID),
                    bipf.dumps(appName),
                    bipf.dumps(appDesc),
                    bipf.dumps(developerID),
                    bipf.dumps(status),
                    bipf.dumps(newDetails)
                ]
                encodedCuratorList = bipf.dumps(curatorList)
                if encodedCuratorList is not None:
                    print(f"ENCODED LIST BIPF {encodedCuratorList.hex()}")
                if r is not None:
                    r.write_new(encodedCuratorList, SigningKey(bytes.fromhex(curatorPrivateKey)))
                    return 1
                else:
                    pass
    print("App not found")
    return None

def updateAppDesc(appNameSearch: str, newDesc: str):

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
    #get private key from the devCurator.json file
    curatorPrivateKey = data.get(curatorfid)
    
    curatorFidBytes = bytes.fromhex(curatorfid)

    appDevID = curatorFidBytes.hex()

    r = replica.Replica("./data", curatorFidBytes, dev.verify_fct)
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
            appFeedID = decodedElements[1]
            appName = decodedElements[2]
            appDesc = decodedElements[3]
            developerID = decodedElements[4]
            status = decodedElements[5]
            details = decodedElements[6]
            if appName == appNameSearch:
                details = "{}"
                curatorList = [
                    bipf.dumps("DevApp"),
                    bipf.dumps(appFeedID),
                    bipf.dumps(appName),
                    bipf.dumps(newDesc),
                    bipf.dumps(developerID),
                    bipf.dumps(status),
                    bipf.dumps(details)
                ]
                encodedCuratorList = bipf.dumps(curatorList)
                if encodedCuratorList is not None:
                    print(f"ENCODED LIST BIPF {encodedCuratorList.hex()}")
                if r is not None:
                    r.write_new(encodedCuratorList, SigningKey(bytes.fromhex(curatorPrivateKey)))
                    return 1
                else:
                    pass
    print("App not found")
    return None

def updateAppStatus(appNameSearch: str, newStatus: str):

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
    #get private key from the devCurator.json file
    curatorPrivateKey = data.get(curatorfid)
    
    curatorFidBytes = bytes.fromhex(curatorfid)

    appDevID = curatorFidBytes.hex()

    r = replica.Replica("./data", curatorFidBytes, dev.verify_fct)
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
            appFeedID = decodedElements[1]
            appName = decodedElements[2]
            appDesc = decodedElements[3]
            developerID = decodedElements[4]
            status = decodedElements[5]
            details = decodedElements[6]
            if appName == appNameSearch:
                details = "{}"
                curatorList = [
                    bipf.dumps("DevApp"),
                    bipf.dumps(appFeedID),
                    bipf.dumps(appName),
                    bipf.dumps(appDesc),
                    bipf.dumps(developerID),
                    bipf.dumps(newStatus),
                    bipf.dumps(details)
                ]
                encodedCuratorList = bipf.dumps(curatorList)
                if encodedCuratorList is not None:
                    print(f"ENCODED LIST BIPF {encodedCuratorList.hex()}")
                if r is not None:
                    r.write_new(encodedCuratorList, SigningKey(bytes.fromhex(curatorPrivateKey)))
                    return 1
                else:
                    pass
    print("App not found")
    return None

def readCuratorFeed(seq: str):
    
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

    if curatorfid is None:
        print("Curator Feed not found")
        return None
    else:
        r = replica.Replica("./data", bytes.fromhex(curatorfid), dev.verify_fct)
        entry = r.read(int(seq))

        if entry:
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
                print(f"App Feed ID: {appFeedID.hex()}")
                print(f"App Name: {appName}")
                print(f"App Description: {appDesc}")
                print(f"Developer ID: {developerID}")
                print(f"Status: {status}")
                print(f"Details: {details}")
            else:
                pass
            
def createCuratorFeed():

    keypair = create_keypair()
    signingKey = keypair[0]
    verifyKey = keypair[1]
    fid = verifyKey.vk_s

    #check if a keypaid exists in devCurator.json
    file_path = "devCurator.json"
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
    
    r = replica.Replica("./data", fid, dev.verify_fct)
    r.state['max_seq'] = 0
    print(r.state['max_seq'])
    print(f"New Replica Created {fid.hex()}")
    dev.updateAppKeys(verifyKey.vk_s, signingKey.sk_s)
    
    # Create the list to be encoded
    curatorList = [
        bipf.dumps("DevCuratorFeed"),
        bipf.dumps(fid),
    ]

    file_path = "devCurator.json"
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
