package nz.scuttlebutt.tremolavossbol

import android.util.Log
import nz.scuttlebutt.tremolavossbol.crypto.SodiumAPI
import nz.scuttlebutt.tremolavossbol.utils.Bipf
import nz.scuttlebutt.tremolavossbol.utils.Bipf_e
import nz.scuttlebutt.tremolavossbol.utils.HelperFunctions.Companion.decodeHex
import nz.scuttlebutt.tremolavossbol.utils.HelperFunctions.Companion.toHex
import org.json.JSONObject
import java.io.File
import kotlin.reflect.jvm.internal.impl.types.AbstractTypeCheckerContext.SupertypesPolicy.None

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

    fun listCuratorApps(fid: String): ArrayList<String> {
        val r = act.tinyRepo.fid2replica(fid.decodeHex())
        val appList = ArrayList<String>()
        val appNameList = ArrayList<String>()
        val lastSeq = r?.state?.max_seq
        if (lastSeq != null) {
            for (i in lastSeq downTo 1) {
                val entry = r?.read_content(i)
                val entryType = entry?.let { getFromEntry(it, 0) }
                if (entryType == "DevApp") {
                    if (entry is ByteArray) {
                        val appFeedID = getFromEntry(entry, 1)
                        val appName = getFromEntry(entry, 2)
                        val appDesc = getFromEntry(entry, 3)
                        val developerID = getFromEntry(entry, 4)
                        val status = getFromEntry(entry, 5)
                        val details = getFromEntry(entry, 6)
                        if (!appNameList.contains(appName)) {
                            appNameList.add(appName.toString())
                            appList.add(appDesc.toString())
                        }
                    }
                }
            }
        }
        return appNameList
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

    fun restoreVersion() {
        //TODO
        //Function to get release version of an App
        //Should update the current files with the files belonging to a release
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