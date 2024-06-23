package nz.scuttlebutt.tremolavossbol

import android.util.Log
import nz.scuttlebutt.tremolavossbol.crypto.SodiumAPI
import nz.scuttlebutt.tremolavossbol.tssb.AppConnector
import nz.scuttlebutt.tremolavossbol.utils.Bipf
import nz.scuttlebutt.tremolavossbol.utils.HelperFunctions.Companion.decodeHex
import nz.scuttlebutt.tremolavossbol.utils.HelperFunctions.Companion.toHex
import org.json.JSONArray
import org.json.JSONObject
import java.io.File
import java.nio.file.Paths

data class AppData(
    val appFeedIDList: ArrayList<String>,
    val appNameList: ArrayList<String>,
    val appDescList: ArrayList<String>,
    val developerIDList: ArrayList<String>,
    val statusList: ArrayList<String>,
)

data class ReleaseData(
    val versionList: ArrayList<String>,
    val commentList: ArrayList<String>,
)


class AppDevInterface(val act: MainActivity) {

    fun createAppFeed(appName: String, appDesc: String) {
        val keypair = SodiumAPI.lazySodiumInst.cryptoSignKeypair()
        val signingKey = keypair.secretKey.asBytes
        val verifyKey = keypair.publicKey.asBytes
        val fid = verifyKey
        Log.d("SIGNING KEY", keypair.secretKey.asBytes.toHex())
        act.tinyRepo.add_replica(fid)
        Log.d("New Replica", "Created Replica " + fid.toHex())
        updateAppKeys(verifyKey, signingKey)
        val AppCreateList = ArrayList<Any>()
        AppCreateList.add(Bipf.mkString("APP"))
        AppCreateList.add(Bipf.mkBytes(fid))
        AppCreateList.add(Bipf.mkString("C"))
        AppCreateList.add(Bipf.mkString(appName))
        AppCreateList.add(Bipf.mkString(appDesc))
        val bipfCreateList = Bipf.mkList(AppCreateList)
        val encodedCreateList = Bipf.encode(bipfCreateList)
        if (encodedCreateList != null) {
            Log.d("ENCODED LIST BIPF", encodedCreateList.toHex())
        }
        val r = act.tinyRepo.fid2replica(fid)
        val lastSeq = r?.state?.max_seq
        if (encodedCreateList != null) {
            if (r != null) {
                val attempt = r.write(encodedCreateList, signingKey)
                Log.d("Attempt", attempt.toString())
            }
        }
    }

    fun readFromFeed(fid: String, sequence: Int) {
        val fid = fid.decodeHex()
        val r = act.tinyRepo.fid2replica(fid)
        val content = r?.read_content(sequence.toInt())
        if (content != null) {
            try {
                val decodedPkt = Bipf.decode(content)
                if (decodedPkt != null) {
                    if (decodedPkt.typ == 4) { //If packet is a list
                        val readablePkt = decodedPkt?.get()?.toString() ?: "Error decoding packet"
                        val pktType = Bipf.decodeListElement(decodedPkt, 0)

                        Log.d("Read Packet", readablePkt)

                        when (pktType) {
                            "APP" -> {
                                // App entry
                            }
                            "A" -> {
                                //Asset entry
                                val asset = Bipf.decodeListElement(decodedPkt, 1)
                                if (asset is ByteArray) {
                                    Log.d("APP Requested Asset", asset.toHex())
                                }
                            }
                            "R" -> {
                                // Release entry
                                val dict = Bipf.decodeListElement(decodedPkt, 1) as? Map<*, *>
                                if (dict != null) {
                                    val version = dict["version"]
                                    val assets = dict["assets"] as? Map<*, *>
                                    val comment = dict["comment"] as? String
                                    Log.d("Release Dictionary", dict.toString())
                                    if (comment != null) {
                                        Log.d("Release Comment", comment)
                                    }
                                }
                            }
                        }
                    }
                }

            } catch (e: Exception) {
                Log.d("Packet Error", "Error decoding packet: ${e.message}")
            }
        }
    }

    fun deleteCurator(fid: String) {
        act.tinyRepo.delete_feed(fid.decodeHex())
    }

    private fun updateAppKeys(publicKey: ByteArray, privateKey: ByteArray) {
        //Dictionary with App Public Key as key and App private key as value
        val ctx = act.applicationContext
        val publicKeyHex = publicKey.toHex()
        val privateKeyHex = privateKey.toHex()

        val file = File(ctx.filesDir, "AppSecrets.json")
        val json: JSONObject

        if (file.exists()) {
            val jsonString = file.readText()
            json = JSONObject(jsonString)
        } else {
            json = JSONObject()
        }

        json.put(publicKeyHex, privateKeyHex)

        file.writeText(json.toString())
    }

    fun getAppName(fid: String): String {
        val ctx = act.applicationContext
        val r = act.tinyRepo.fid2replica(fid.decodeHex())
        val firstEntry = r?.read_content(1)
        val firstEntryType = firstEntry?.let { getFromEntry(it, 0) }
        if (firstEntryType == "APP") {
            return getFromEntry(firstEntry, 2).toString()
        }
        return ""
    }

    fun getAllAppFeeds() {
        val feeds = act.tinyRepo.listFeeds()
        val feedList = ArrayList<String>()
        val appList = ArrayList<String>()
        for (feed in feeds) {
            try {
                val r = act.tinyRepo.fid2replica(feed)
                val firstEntry = r?.read_content(1)
                val firstEntryType = firstEntry?.let { getFromEntry(it, 0) }
                if (firstEntryType == "APP") {
                    appList.add(getFromEntry(firstEntry, 2).toString())
                    val listOfApps = listCuratorApps(feed.toHex());
                    Log.d("listApps", listOfApps.toString())

                }

            } catch (e: Exception) {
                Log.d("Feed Exception", "Could not read feed" + feed.toHex())
            }
        }
        Log.d("AppsFeedRequest", appList.toString())
    }

    fun getAppStatus(fid: String): Int {
        //first we check if the app is downloaded (if it exists in appdata), if yes return 1
        val ctx = act.applicationContext
        val appsInterface = AppsInterface(ctx)

        if (appsInterface.checkIfAppExists(fid)) {
            return 1
        }

        //then we check if the appFeed is present (if it is present in feeds), if yes return 2
        else {
            val feeds = act.tinyRepo.listFeeds()
            for (feed in feeds) {
                if (feed.toHex() == fid) {
                    return 2
                }
            }
        }

        //else return -1
        return -1
    }

    fun pullApp(appID: String, curatorID: String) {
        val appKey = appID.decodeHex()
        val appLinks = getAppLinks(curatorID, appID)
        val firstLink = appLinks[0]

        act.tinyRepo.context.tinyGoset._remove_all_keys()
        act.tinyRepo.context.tinyGoset._add_key(appKey)
        act.tinyRepo.context.connect_mode = 2
        act.tinyRepo.context.original_websocket = act.settings!!.getWebsocketUrl()

        act.settings?.setWebsocketUrl(firstLink)
        act.websocket?.start()
        
        Log.d("test", act.tinyRepo.context.tinyGoset.keys.size.toString())
    }

    fun pullCurator(curatorLink: String) {

        act.tinyRepo.context.tinyGoset._remove_all_keys()
        act.tinyRepo.context.connect_mode = 1

        act.tinyRepo.context.original_websocket = act.settings!!.getWebsocketUrl()

        act.settings?.setWebsocketUrl(curatorLink)
        act.websocket?.start()

        Log.d("test", act.tinyRepo.context.tinyGoset.keys.size.toString())
    }

    fun getAppLinks(curatorID: String, appID: String): ArrayList<String> {
        val r = act.tinyRepo.fid2replica(curatorID.decodeHex())
        val linksList = ArrayList<String>()
        val lastSeq = r?.state?.max_seq
        if (lastSeq != null) {
            for (i in lastSeq downTo 1) {
                val entry = r?.read_content(i)
                val entryType = entry?.let { getFromEntry(it, 0) }
                if (entryType == "DevApp") {
                    if (entry is ByteArray) {
                        val appFeedID = getFromEntry(entry, 1)
                        if (appFeedID is ByteArray) {
                            val appFeedIDHex = appFeedID.toHex()
                            if (appFeedIDHex == appID) {
                                val details = getFromEntry(entry, 6)
                                // Extract URL from JSON string
                                val jsonObject = JSONObject(details.toString())
                                var url = ""
                                if (jsonObject.has("url")) {
                                    url = jsonObject.getString("url")
                                    // Parse the JSON string
                                    val jsonArray = JSONArray(url)
                                    // Convert the JSONArray to a Kotlin Array
                                    val linksArray = Array(jsonArray.length()) { i -> jsonArray.getString(i) }
                                    for (url in linksArray) {
                                        linksList.add(url)
                                    }
                                    return linksList
                                }
                            }
                        }
                    }
                }
            }
        }
        return linksList
    }

    fun listAppVersions(fid: String) : ReleaseData {
        val versionList = ArrayList<String>()
        val commentList = ArrayList<String>()
        val r = act.tinyRepo.fid2replica(fid.decodeHex())
        val lastSeq = r?.state?.max_seq
        if (lastSeq != null) {
            for (i in 1 until  lastSeq + 1) {
                val entry = r?.read_content(i)
                val entryType = entry?.let { getFromEntry(it, 0) }
                if (entryType == "R") {
                    if (entry is ByteArray) {
                        val version = getFromEntry(entry, 1)
                        val assets = getFromEntry(entry, 2)
                        val comment = getFromEntry(entry, 3)
                        versionList.add(version.toString())
                        commentList.add(comment.toString())
                        Log.d("Details App Releases (Version)", version.toString())
                        Log.d("Details App Releases (Assets)", assets.toString())
                        Log.d("Details App Releases (Comment)", comment.toString())
                    }
                }
            }
        }
        return ReleaseData(versionList, commentList)
    }

    fun getReleaseSequence(fid: String, version: String): Int {
        val r = act.tinyRepo.fid2replica(fid.decodeHex())
        val lastSeq = r?.state?.max_seq

        if (lastSeq != null) {
            for (i in 1 until  lastSeq + 1) {
                val entry = r?.read_content(i)
                val entryType = entry?.let { getFromEntry(it, 0) }
                if (entryType == "R") {
                    if (entry is ByteArray) {
                        val found_version = getFromEntry(entry, 1)
                        if (found_version == version) {
                            return i
                        }
                    }
                }
            }
        }
        return -1
    }

    fun downloadAppVersion(fid: String, version: String) {
        val r = act.tinyRepo.fid2replica(fid.decodeHex())
        val seq = getReleaseSequence(fid, version)

        if (seq == -1) {
            Log.d("Download Error", "Could not find App Version")
            return
        }
        val entry = r?.read_content(seq)
        val entryType = entry?.let { getFromEntry(it, 0) }
        if (entryType == "R") {
            if (entry is ByteArray) {
                val version = getFromEntry(entry, 1)
                var assets = getFromEntry(entry, 2)
                val comment = getFromEntry(entry, 3)
                Log.d("Details App Releases (Version)", version.toString())
                Log.d("Details App Releases (Assets)", assets.toString())
                Log.d("Details App Releases (Comment)", comment.toString())

                val ctx = act.applicationContext
                val appsInterface = AppsInterface(ctx)

                val appPath = appsInterface.getAppDirectoryPath()

                appsInterface.removeApp(fid)

                appsInterface.createDirectory(appPath, fid)

                assets = JSONObject(assets.toString())

                val keys: Iterator<String> = assets.keys()
                while (keys.hasNext()) {
                    val assetName = keys.next()
                    val assetSeq = assets.get(assetName)
                    getAndDownloadAsset(fid, assetSeq as Int, Paths.get(appPath, fid, assetName).toString(), assetName)
                }

            }

        }
    }

    fun getAndDownloadAsset(fid: String, assetSeq: Int, path: String, fileName: String) {
        val r = act.tinyRepo.fid2replica(fid.decodeHex())
        val entry = r?.read_content(assetSeq)
        val entryType = entry?.let { getFromEntry(it, 0) }
        if (entryType == "A") {
            if (entry is ByteArray) {
                val asset = getFromEntry(entry, 1)

                val ctx = act.applicationContext
                val appsInterface = AppsInterface(ctx)

                val appPath = appsInterface.getAppDirectoryPath()

                appsInterface.updateApp(fid, fileName, asset)
            }
        }
    }

    fun listCuratorApps(fid: String): AppData {
        val r = act.tinyRepo.fid2replica(fid.decodeHex())
        var localStatus = -99
        val appNameList = ArrayList<String>()
        val appFeedIDList = ArrayList<String>()
        val appDescList = ArrayList<String>()
        val developerIDList = ArrayList<String>()
        val statusList = ArrayList<String>()
        val detailsList = ArrayList<String>()
        val lastSeq = r?.state?.max_seq
        if (lastSeq != null) {
            for (i in lastSeq downTo 1) {
                val entry = r?.read_content(i)
                val entryType = entry?.let { getFromEntry(it, 0) }
                if (entryType == "DevApp") {
                    if (entry is ByteArray) {
                        Log.d("Details AppIdCurator", fid)
                        val appFeedID = getFromEntry(entry, 1)
                        val appName = getFromEntry(entry, 2)
                        val appDesc = getFromEntry(entry, 3)
                        val developerID = getFromEntry(entry, 4)
                        if (appFeedID is ByteArray) {
                            localStatus = getAppStatus(appFeedID.toHex())
                        }
                        val status = getFromEntry(entry, 5)
                        val details = getFromEntry(entry, 6)
                        Log.d("Details AppIdCurator", details.toString())
                        if (!appNameList.contains(appName)) {
                            appNameList.add(appName.toString())
                            appDescList.add(appDesc.toString())
                            detailsList.add(details.toString())

                            // Extract URL from JSON string
                            val jsonObject = JSONObject(details.toString())
                            var url = ""
                            if (jsonObject.has("url")) {
                                url = jsonObject.getString("url")
                            }
                            Log.d("URL mofo", url)
                            if (url != "") {
                                if (localStatus == -1) {
                                    localStatus = 3
                                }
                            }
                            statusList.add(localStatus.toString())

                            if (appFeedID is ByteArray) {
                                appFeedIDList.add(appFeedID.toHex())
                            }
                            if (developerID is ByteArray) {
                                developerIDList.add(developerID.toHex())
                            }
                        }
                    }
                }
            }
        }

        return AppData(appFeedIDList, appNameList, appDescList, developerIDList, statusList)
    }

    fun getAllCuratorFeeds(): ArrayList<String> {
        val feeds = act.tinyRepo.listFeeds()
        val curatorList = ArrayList<String>()
        for (feed in feeds) {
            try {
                val r = act.tinyRepo.fid2replica(feed)
                val firstEntry = r?.read_content(1)
                val firstEntryType = firstEntry?.let { getFromEntry(it, 0) }
                if (firstEntryType == "CuratorFeed") {
                    Log.d("listcuratorsfid", feed.toHex())
                    val curatorFID = getFromEntry(firstEntry, 1)
                    if (curatorFID is ByteArray) {
                        curatorList.add("" + curatorFID.toHex())
                    }
                    Log.d("listaCurators", curatorList.toString())
                }
            } catch (e: Exception) {
                Log.d("Feed Exception", "Could not read feed" + feed.toHex())
            }
        }
        return curatorList
    }

    fun getFromEntry(entry: ByteArray, index: Int): Any? {
        if (entry != null) {
            val entry = Bipf.bipf_loads(entry)
            if (entry != null) {
                if (entry.get() is ArrayList<*>) {
                    val first = (entry.get() as ArrayList<*>).get(index)
                    if (first is ByteArray) {
                        val firstDecoded = Bipf.decode(first)
                        if (firstDecoded != null) {
                            val value = firstDecoded.get()
                            Log.d("afasfasfaf", value.toString())
                            return value
                        }
                    }
                }
            }
        }
        return null
    }

    fun getAppPrivateKey(fid: String): String? {
        val ctx = act.applicationContext
        val file = File(ctx.filesDir, "AppSecrets.json")

        if (!file.exists()) {
            Log.d("App Key Error", "File does not exist.")
            return null
        }

        val jsonString = file.readText()
        val json = JSONObject(jsonString)

        if (json.has(fid)) {
            return json.getString(fid)
        } else {
            Log.d("Key Error", "No private key found for " + fid)
            return null
        }
    }

    fun insertAssetIntoAppFeed(fid: String, asset: ByteArray) {
        if (getAppPrivateKey(fid) == null) {
            Log.d("App Insert Error", "Public Key not valid")
        } else {
            val appInsertList = ArrayList<Any>()
            appInsertList.add(Bipf.mkString("A"))
            appInsertList.add(Bipf.mkBytes(asset))
            val bipfInsertList = Bipf.mkList(appInsertList)
            val encodedInsertList = Bipf.encode(bipfInsertList)
            val r = act.tinyRepo.fid2replica(fid.decodeHex())
            val lastSeq = r?.state?.max_seq
            if (encodedInsertList != null) {
                Log.d("ENCODED LIST BIPF", encodedInsertList.toHex())
                if (r != null) {
                    getAppPrivateKey(fid)?.let { r.write(encodedInsertList, it.decodeHex()) }
                }
            }
        }
    }

    fun insertReleaseIntoAppFeed(fid: String, version: String, comment: String) {
        //TODO
        if (getAppPrivateKey(fid) == null) {
            Log.d("App Insert Error", "Public Key not valid")
        } else {
            val appInsertList = ArrayList<Any>()
            appInsertList.add(Bipf.mkString("R"))
            val releaseDictionary = Bipf.mkDict()
            Bipf.dict_append(releaseDictionary, Bipf.mkString("version"), Bipf.mkString(version))
            val assetsDictionary = Bipf.mkDict()
            Bipf.dict_append(assetsDictionary, Bipf.mkString("AppSecrets.json"), Bipf.mkInt(2))
            Bipf.dict_append(releaseDictionary, Bipf.mkString("assets"), assetsDictionary)
            Bipf.dict_append(releaseDictionary, Bipf.mkString("comment"), Bipf.mkString(comment))

            appInsertList.add(releaseDictionary)
            val bipfInsertList = Bipf.mkList(appInsertList)
            val encodedInsertList = Bipf.encode(bipfInsertList)
            val r = act.tinyRepo.fid2replica(fid.decodeHex())
            val lastSeq = r?.state?.max_seq
            if (encodedInsertList != null) {
                Log.d("ENCODED LIST BIPF", encodedInsertList.toHex())
                if (r != null) {
                    getAppPrivateKey(fid)?.let { r.write(encodedInsertList, it.decodeHex()) }
                }
            }
        }
    }

    fun fileToByteArray(fileName: String): ByteArray? {
        val ctx = act.applicationContext
        try {
            val file = File(ctx.filesDir, fileName)
            return file.readBytes()
        } catch (e: Exception) {
            Log.d("App File Error", e.stackTraceToString())
            return null
        }
    }
}