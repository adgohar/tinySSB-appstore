package nz.scuttlebutt.tremolavossbol

import android.util.Log
import nz.scuttlebutt.tremolavossbol.crypto.SodiumAPI
import nz.scuttlebutt.tremolavossbol.utils.Bipf
import nz.scuttlebutt.tremolavossbol.utils.HelperFunctions.Companion.decodeHex
import nz.scuttlebutt.tremolavossbol.utils.HelperFunctions.Companion.toHex
import org.json.JSONObject
import java.io.File
import java.nio.file.Files

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
            Log.d("Packet (non-edited)", content.toHex())
            try {
                // Decode the packet using Bipf
                val decodedPkt = Bipf.decode(content)
                if (decodedPkt != null) {
                    if (decodedPkt.typ == 4) { //If packet is a list
                        val readablePkt = if (decodedPkt != null) decodedPkt.get().toString() else "Error decoding packet"
                        if (Bipf.decodeListElement(decodedPkt, 0) == "APP") {
                            Log.d("Read Packet", readablePkt)
                        } else if (Bipf.decodeListElement(decodedPkt, 0) == "A") {
                            val asset = Bipf.decodeListElement(decodedPkt, 1)
                            if (asset is ByteArray)
                                Log.d("APP Requested Asset", asset.toHex())
                        }
                    }
                }

            } catch (e: Exception) {
                Log.d("Packet Error", "Error decoding packet: ${e.message}")
            }
        }
    }

    fun updateAppKeys(publicKey: ByteArray, privateKey: ByteArray) {
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
                if (firstEntry?.let { Bipf.decode(it)?.let { Bipf.decodeListElement(it, 0) } } == "APP") {
                    feedList.add(feed.toHex())
                    Bipf.decode(firstEntry)
                        ?.let { Bipf.decodeListElement(it, 2).toString() }?.let { appList.add(it) }
                }
            } catch (e: Exception) {
                Log.d("Feed Exception", "Could not read feed" + feed.toHex())
            }
        }
        Log.d("AppsFeedRequest", appList.toString())
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

    fun insertReleaseIntoAppFeed() {
        //TODO
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