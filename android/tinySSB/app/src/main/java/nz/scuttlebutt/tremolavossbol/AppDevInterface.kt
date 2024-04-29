package nz.scuttlebutt.tremolavossbol

import android.util.Log
import nz.scuttlebutt.tremolavossbol.crypto.SodiumAPI
import nz.scuttlebutt.tremolavossbol.utils.Bipf
import nz.scuttlebutt.tremolavossbol.utils.HelperFunctions.Companion.decodeHex
import nz.scuttlebutt.tremolavossbol.utils.HelperFunctions.Companion.toHex

class AppDevInterface(val act: MainActivity) {

    fun createAppFeed(appName: String, appDesc: String) {
        val keypair = SodiumAPI.lazySodiumInst.cryptoSignKeypair()
        val signingKey = keypair.secretKey.asBytes
        val verifyKey = keypair.publicKey.asBytes
        val fid = verifyKey
        Log.d("SIGNING KEY", keypair.secretKey.asBytes.toHex())
        act.tinyRepo.add_replica(fid)
        Log.d("New Replica", "Created Replica " + fid.toHex())
        val AppCreateList = ArrayList<Any>()
        AppCreateList.add(Bipf.mkString("APP"))
        AppCreateList.add(Bipf.mkBytes(fid))
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
                // You might want to convert the decoded packet into a JSON format or a readable string
                val readablePkt = if (decodedPkt != null) decodedPkt.get().toString() else "Error decoding packet"
                Log.d("Read Packet", readablePkt)
            } catch (e: Exception) {
                Log.d("Packet Error", "Error decoding packet: ${e.message}")
            }
        }
    }

    fun getAllAppFeeds() {
        //TODO
    }

    fun updateAppFeed() {
        //TODO
    }

    fun updateAppKeys() {
        //TODO
        //Dictionary with App Public Key as key and App private key as value
    }

    fun restoreVersion() {
        //TODO
        //Function to get release version of an App
        //Should update the current files with the files belonging to a release
    }
}