import sys
import json
import os
from pure25519 import SigningKey, VerifyingKey, create_keypair, open as open25519
from simplepub import bipf, replica
from simplepub.bipf import _dec_list

def developer():
    print("This is the developer function from the developer.py file")

def test():
    print("This is the test function from the developer.py file")

def verify_fct(fid, signature, message):
    print(f"Verifying {signature} {message}")
    return (open25519(signature + message, fid) != None)  #wichtig

def getFeedID(appName: str):
    #go through all folders in the data directory and for each folder get the first entry
    #if the first entry is an app entry and the name matches the appName return the feedID
    
    for folder in os.listdir("data"):
        fid = bytes.fromhex(folder)
        r = replica.Replica("./data", fid, verify_fct)
        foundAppName = getAppName(fid.hex())
        if foundAppName == appName:
            return fid.hex()
        else:
            pass
    return None

def createAppFeed(appName: str, appDesc: str):
    keypair = create_keypair()
    signingKey = keypair[0]
    verifyKey = keypair[1]
    fid = verifyKey.vk_s
    print(f"SIGNING KEY {signingKey.sk_s.hex()}")
    print(f"VERIFY KEY {verifyKey.vk_s.hex()}")    
    
    r = replica.Replica("./data", fid, verify_fct)
    print(f"New Replica Created {fid.hex()}")
    updateAppKeys(verifyKey.vk_s, signingKey.sk_s)
    
    # Create the list to be encoded
    appCreateList = [
        bipf.dumps("APP"),
        bipf.dumps(fid),
        bipf.dumps(appName),
        bipf.dumps(appDesc)
    ]

    # Encode the list of encoded elements
    encodedCreateList = bipf.dumps(appCreateList)
    
    if encodedCreateList is not None:
        print(f"ENCODED LIST BIPF {encodedCreateList.hex()}")
    
    lastSeq = r.state['max_seq']
    if encodedCreateList is not None:
        if r is not None:            
            attempt = r.write_new(encodedCreateList, signingKey)
            print(f"Attempt {attempt}")

def showReleases(appName: str):
    fid = getFeedID(appName)
    if fid is None:
        print("App not found")
        return None
    else:

        r = replica.Replica("./data", bytes.fromhex(fid), verify_fct)
        lastSeq = r.state['max_seq']

        releases = []

        for i in range(1, lastSeq + 1):
            entry = r.read(i)
            decodedEntry, _ = bipf.decode(entry)
            decodedElements = []

            for element in decodedEntry:
                decodedElement, _ = bipf.decode(element)
                decodedElements.append(decodedElement)

            firstElementStr = decodedElements[0]

            if firstElementStr == "R":
                release = decodedElements[1]
                version = release.get("version")
                comment = release.get("comment")
                releases.append(release)
            else:
                pass
        return releases
    
def setActiveRelease(appName: str, release: str):
    fid = getFeedID(appName)
    if fid is None:
        print("App not found")
        return None
    else:

        r = replica.Replica("./data", bytes.fromhex(fid), verify_fct)
        
        seq = getReleaseSequence(fid, release)
        if seq is None:
            print("Release not found")
            return None
        else:
            #copy the release into a new entry in the app feed
            release = getRelease(fid, seq)
            version = release.get("version")
            comment = release.get("comment")
            assets = release.get("assets")
            insertReleaseIntoAppFeed(fid, version, comment, assets)
            print(f"Release {release} set as active")
            
    return None

def getActiveRelease(appName: str):
    fid = getFeedID(appName)
    if fid is None:
        print("App not found")
        return None
    else:

        r = replica.Replica("./data", bytes.fromhex(fid), verify_fct)
        lastSeq = r.state['max_seq']

        #get the last entry with "R", loop backwards
        for i in range(lastSeq, 0, -1):
            entry = r.read(i)
            decodedEntry, _ = bipf.decode(entry)
            decodedElements = []

            for element in decodedEntry:
                decodedElement, _ = bipf.decode(element)
                decodedElements.append(decodedElement)

            firstElementStr = decodedElements[0]

            if firstElementStr == "R":
                release = decodedElements[1]
                version = release.get("version")
                comment = release.get("comment")
                return release
            else:
                pass



def updateAppKeys(publicKey: bytearray, privateKey: bytearray):
    publicKeyHex = publicKey.hex()
    privateKeyHex = privateKey.hex()

    file_path = "AppSecrets.json"
    data = {}

    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            try:
                data = json.load(file)
            except json.JSONDecodeError:
                data = {}

    data[publicKeyHex] = privateKeyHex

    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)

def getAppPrivateKey(publicKey: hex):

    file_path = "AppSecrets.json"
    data = {}

    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            try:
                data = json.load(file)
            except json.JSONDecodeError:
                data = {}

    privateKeyHex = data.get(publicKey)

    if privateKeyHex is not None:
        return bytes.fromhex(privateKeyHex)
    else:
        return None

def fileToBytearray(file_path: str):
    with open(file_path, "rb") as file:
        fileBytes = bytearray(file.read())
    return fileBytes

def commitApp(appName: str, appPath: str, version: str, comment: str):
    fid = getFeedID(appName)
    if fid is None:
        print("App not found")        
    else:
        #map the sequence of each file to the file name
        files = {}
        for file in os.listdir(appPath):
            #if file size is bigger than 100KB, return an error
            if os.path.getsize(os.path.join(appPath, file)) > 100000:
                print(f"File {file} is too big, max size is 100KB. Edit and try again")
                return None
        #loop through each file in the appPath and insert it into the app feed
        for file in os.listdir(appPath):
            #if file size is bigger than 100KB, return an error
            seq = insertAssetIntoAppFeed(fid, os.path.join(appPath, file))
            files[file] = seq
            print(f"File {file} inserted at sequence {seq}")

        #convert the files dictionary to a json string
        files_json = json.dumps(files)


        #insert the release into the app feed
        insertReleaseIntoAppFeed(fid, version, comment, files_json)
        
def insertAssetIntoAppFeed(fid_hex: str, path: str):
    fid = bytes.fromhex(fid_hex)
    privateKey = getAppPrivateKey(fid.hex())
    asset = fileToBytearray(path)

    if privateKey is None:
        print("Public Key not valid")
        return None

    signingKey = SigningKey(privateKey)
    # Create the list to be encoded, converting bytearray to bytes
    appInsertList = [
        bipf.dumps("A"),
        bipf.dumps(bytes(asset))
    ]

    # Encode the list of elements using BIPF
    encodedInsertList = bipf.dumps(appInsertList)

    r = replica.Replica("./data", fid, verify_fct)
    lastSeq = r.state['max_seq']

    # Check if an identical asset already exists in the feed
    for seq in range(1, lastSeq + 1):
        try:
            existing_entry = r.read(seq)
            if existing_entry and bipf.loads(existing_entry) == appInsertList:
                return seq
        except Exception as e:
            print(f"Error retrieving sequence {seq}: {e}")

    # If no identical asset is found, insert the new asset
    if encodedInsertList is not None:
        attempt = r.write_new(encodedInsertList, signingKey)
        return attempt

    return None

def insertReleaseIntoAppFeed(fid_hex: str , version: str, comment: str, files_json: str):
    fid = bytes.fromhex(fid_hex)
    privateKey = getAppPrivateKey(fid.hex())
    
    if privateKey is None:
        print("Public Key not valid")
    else:
        signingKey = SigningKey(privateKey)

        #files = json.loads(files_json)
        files = files_json

        # Create the list to be encoded
        appInsertList = [
            bipf.dumps("R"),
            bipf.dumps({
                "version": version,
                "assets": files,
                "comment": comment
            })
        ]
        # Encode the list of encoded elements
        encodedInsertList = bipf.dumps(appInsertList)
        
        r = replica.Replica("./data", fid, verify_fct)
        lastSeq = r.state['max_seq']
        
        if encodedInsertList is not None:
            print(f"ENCODED LIST BIPF {encodedInsertList.hex()}")
            if r is not None:
                r.write_new(encodedInsertList, signingKey)

def getAppName(fid_hex: str):
    fid = bytes.fromhex(fid_hex)

      # Dummy verification function

    r = replica.Replica("./data", fid, verify_fct)
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

        #print(f"Decoded Elements: {decodedElements}")

        firstElementStr = decodedElements[0]

        if firstElementStr == "APP":
            appName = decodedElements[2]
            return appName
        else:
            pass
    else:
        pass

def getAndDownloadAsset(fid_hex: str, seq: str, path: str):
    fid = bytes.fromhex(fid_hex)

      # Dummy verification function

    r = replica.Replica("./data", fid, verify_fct)
    entry = r.read(int(seq))

    if entry:
        decodedEntry, _ = bipf.decode(entry)
        decodedElements = []

        for element in decodedEntry:
            decodedElement, _ = bipf.decode(element)
            decodedElements.append(decodedElement)

        #print(f"Decoded Elements: {decodedElements}")

        firstElementStr = decodedElements[0]

        if firstElementStr == "A":
            asset = decodedElements[1]
            with open(path, "wb") as file:
                file.write(asset)
            print(f"Asset downloaded to {path}")
        else:
            print(f"First element is not 'A', it's {firstElementStr}")
    else:
        print("Invalid or no entry found")

def downloadApp(appName: str, path: str, release: str=None):
    fid = getFeedID(appName)
    fid_bytes = bytes.fromhex(fid)
    if fid is None:
        print("App not found")
        return None
    else:
        
        if release == None:
            release = getActiveRelease(appName)
            release = release.get("version")

        r = replica.Replica("./data", fid_bytes, verify_fct)
        seq = getReleaseSequence(fid, release)
        if seq is None:
            print("Release not found")
            return None
        entry = r.read(int(seq))

        if entry:
            decodedEntry, _ = bipf.decode(entry)
            decodedElements = []

            for element in decodedEntry:
                decodedElement, _ = bipf.decode(element)
                decodedElements.append(decodedElement)

            firstElementStr = decodedElements[0]

            if firstElementStr == "R":
                release = decodedElements[1]
                print(f"Release: {release}")
                #Release: {'version': '1.1', 'assets': '{"Basel Wappen.png": 2, "FNA.csv": 3, "Suva Pr\\u00e4si.pdf": 4}', 'comment': 'This is my First Release'}
                #go through the assets and download them
                assets = json.loads(release.get("assets"))
                #now clear old folder, delete every file there
                for file in os.listdir(path):
                    os.remove(os.path.join(path, file))
                for asset in assets:
                    assetSeq = assets[asset]
                    getAndDownloadAsset(fid, assetSeq, os.path.join(path, asset))
                print(f"Release downloaded to {path}")
            else:
                print(f"First element is not 'R', it's {firstElementStr}")
        else:
            print("Invalid or no entry found")

def getReleaseSequence(fid_hex: str, release: str):
    fid = bytes.fromhex(fid_hex)

      # Dummy verification function

    r = replica.Replica("./data", fid, verify_fct)
    lastSeq = r.state['max_seq']

    for i in range(1, lastSeq + 1):
        entry = r.read(i)
        decodedEntry, _ = bipf.decode(entry)
        decodedElements = []

        for element in decodedEntry:
            decodedElement, _ = bipf.decode(element)
            decodedElements.append(decodedElement)

        firstElementStr = decodedElements[0]

        if firstElementStr == "R":
            found_release = decodedElements[1]            
            found_version = found_release.get("version")

            if found_version == release:
                print(f"Release found at sequence {i}")
                return i
        else:
            pass

    return None

def getRelease(fid_hex: str, seq: str):
    fid = bytes.fromhex(fid_hex)

      # Dummy verification function

    r = replica.Replica("./data", fid, verify_fct)
    entry = r.read(int(seq))

    if entry:
        decodedEntry, _ = bipf.decode(entry)
        decodedElements = []

        for element in decodedEntry:
            decodedElement, _ = bipf.decode(element)
            decodedElements.append(decodedElement)

        firstElementStr = decodedElements[0]

        if firstElementStr == "R":
            release = decodedElements[1]
            print(f"Release: {release}")
            return release
        else:
            print(f"First element is not 'R', it's {firstElementStr}")
    else:
        print("Invalid or no entry found")

def endApp(appName: str, comment: str=None):
    #Add a new entry with "D" at the start of the app feed and the comment
    fid = getFeedID(appName)
    if fid is None:
        print("App not found")
        return None
    else:

        r = replica.Replica("./data", bytes.fromhex(fid), verify_fct)
        lastSeq = r.state['max_seq']

        # Create the list to be encoded
        appEndList = [
            bipf.dumps("D"),
            bipf.dumps(comment)
        ]

        # Encode the list of encoded elements
        encodedEndList = bipf.dumps(appEndList)

        if encodedEndList is not None:
            print(f"ENCODED LIST BIPF {encodedEndList.hex()}")

        if r is not None:
            r.write_new(encodedEndList , SigningKey(getAppPrivateKey(fid)))
            print(f"App {appName} ended")
            return None
        
def getAppStatus(appName: str):
    #if last entry is "D" then the app is ended, else it's active
    fid = getFeedID(appName)
    if fid is None:
        print("App not found")
        return None
    else:
        r = replica.Replica("./data", bytes.fromhex(fid), verify_fct)
        lastSeq = r.state['max_seq']

        entry = r.read(lastSeq)
        decodedEntry, _ = bipf.decode(entry)
        decodedElements = []

        for element in decodedEntry:
            decodedElement, _ = bipf.decode(element)
            decodedElements.append(decodedElement)

        firstElementStr = decodedElements[0]

        if firstElementStr == "D":
            print(f"App {appName} is ended")
            return "ended"
        else:
            print(f"App {appName} is active")
            return "active"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 developer.py [command]")
        sys.exit(1)
    #Get the function name from the command line
    function_name = sys.argv[1]

    #Check if the function exists
    if function_name not in globals():
        print(f"Command {function_name} not found, available commands:")
        print("\n".join([f for f in globals() if callable(globals()[f])]))
        sys.exit(1)

    #Call the function with arguments if any
    if len(sys.argv) > 2:
        globals()[function_name](*sys.argv[2:])
    else:
        globals()[function_name]()