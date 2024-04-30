package nz.scuttlebutt.tremolavossbol

import android.util.Log
import nz.scuttlebutt.tremolavossbol.utils.Bipf
import nz.scuttlebutt.tremolavossbol.utils.Bipf_e
import nz.scuttlebutt.tremolavossbol.utils.HelperFunctions.Companion.decodeHex
import nz.scuttlebutt.tremolavossbol.utils.HelperFunctions.Companion.toHex
import java.io.File

class ManageAppsInterface (val act: MainActivity) {

    fun getAllAppFeeds(): MutableMap<String, String> {
        val appMapping = mutableMapOf<String, String>()
        val feeds = act.tinyRepo.listFeeds()
        for (feed in feeds) {
            try {
                val r = act.tinyRepo.fid2replica(feed)
                val firstEntry = r?.read_content(1)
                if (firstEntry?.let { Bipf.decode(it)?.let { Bipf.decodeListElement(it, 0) } } == "APP") {
                    val appName = getAppName(feed.toHex())
                    appMapping[feed.toHex()] = appName
                }
            } catch (e: Exception) {
                Log.d("Feed Exception", "Could not read feed" + feed.toHex())
            }
        }
        return appMapping
    }

    fun getAppName(fid: String): String {
        try {
            val r = act.tinyRepo.fid2replica(fid.decodeHex())
            val firstEntry = r?.read_content(1)
            if (firstEntry?.let { Bipf.decode(it)?.let { Bipf.decodeListElement(it, 0) } } == "APP") {
                return Bipf.decodeListElement(Bipf.decode(firstEntry) as Bipf_e, 2).toString()
            } else {
                return "Invalid"
            }
        } catch (e: Exception) {
            Log.d("Feed Exception", "Could not read feed $fid")
            return "Invalid"
        }
    }

    fun getAppReleases(fid: String): MutableMap<String, String> {
        val releaseMapping = mutableMapOf<String, String>()

        val fid = fid.decodeHex()
        val r = act.tinyRepo.fid2replica(fid)

        val maxSeq = r?.state?.max_seq

        for (i in 1 until maxSeq as Int + 1) {
            val content = r?.read_content(i)
            if (content != null) {
                val decodedPkt = Bipf.decode(content)
                if (decodedPkt != null) {
                    val readablePkt = decodedPkt?.get()?.toString() ?: "Error decoding packet"
                    val pktType = Bipf.decodeListElement(decodedPkt, 0)

                    if (pktType == "R") {
                        // Release entry
                        val dict = Bipf.decodeListElement(decodedPkt, 1) as? Map<*, *>
                        if (dict != null) {
                            val version = dict["version"] as? String
                            val assets = dict["assets"] as? Map<*, *>
                            val comment = dict["comment"] as? String
                            if (version != null && comment != null) {
                                releaseMapping.put(fid.toHex() + ";" + version, comment)
                            }
                        }
                    }
                }

            }
        }

        return releaseMapping
    }

    fun getAsset(fid: String, sequence: Int): ByteArray {
        val fid = fid.decodeHex()
        val r = act.tinyRepo.fid2replica(fid)
        val content = r?.read_content(sequence.toInt())
        if (content != null) {
            try {
                val decodedPkt = Bipf.decode(content)
                if (decodedPkt != null) {
                    val readablePkt = decodedPkt?.get()?.toString() ?: "Error decoding packet"
                    val pktType = Bipf.decodeListElement(decodedPkt, 0)
                    if (pktType == "A") {
                        //Asset entry
                        val asset = Bipf.decodeListElement(decodedPkt, 1)
                        if (asset is ByteArray) {
                            return asset
                        }
                    }
                }
            } catch (e: Exception) {
                Log.d("Packet Error", "Error decoding packet: ${e.message}")
            }
        }
        return null as ByteArray
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

    fun activateRelease(fid: String, version: String) {
        val fid = fid.decodeHex()
        val r = act.tinyRepo.fid2replica(fid)

        val maxSeq = r?.state?.max_seq

        for (i in 1 until maxSeq as Int + 1) {
            val content = r?.read_content(i)
            if (content != null) {
                val decodedPkt = Bipf.decode(content)
                if (decodedPkt != null) {
                    val readablePkt = decodedPkt?.get()?.toString() ?: "Error decoding packet"
                    val pktType = Bipf.decodeListElement(decodedPkt, 0)

                    if (pktType == "R") {
                        // Release entry
                        val dict = Bipf.decodeListElement(decodedPkt, 1) as? Map<*, *>
                        if (dict != null) {
                            val foundVersion = dict["version"] as? String
                            if (foundVersion == version) {
                                val assets = dict["assets"] as? Map<String, Int>
                                if (assets != null) {
                                    updateAssets(fid.toHex(), assets)
                                };
                            }
                        }
                    }
                }

            }
        }
    }

    private fun updateAssets(fid: String, assets: Map<String, Int>) {
        val appInterface = AppsInterface(act.applicationContext)
        val appPath = appInterface.getAppDirectoryPath()

        //get App name
        val appName = getAppName(fid)

        val directoryName = fid + ";" + appName

        appInterface.removeApp(directoryName)

        //Create App Directory if it doesn't exist
        val status = appInterface.createDirectory(appPath, directoryName)

        //Loop through assets and create the files
        for ((fileName, feedSeq) in assets) {
            Log.d("APPSTATUS", feedSeq.toString())
            val fileByteArray = getAsset(fid, feedSeq)
            val newAppFolder = File(appPath, directoryName)
            val file = File(newAppFolder, fileName)
            file.writeBytes(fileByteArray)
        }
    }

}