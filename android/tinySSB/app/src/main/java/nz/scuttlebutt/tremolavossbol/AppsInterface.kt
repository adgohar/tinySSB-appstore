package nz.scuttlebutt.tremolavossbol
import java.io.File
import java.util.Base64
import android.content.Context


class AppsInterface (context: Context) {
    private val context = context

    private fun getAppDirectoryPath(): String {
        val appContext = context // Assuming this is called within an Activity or Context
        val filesDir = appContext.filesDir // Path to /data/data/your_app_package_name/files

        // Define the path for the "apps" subdirectory within filesDir
        val appsSubDir = File(filesDir, "apps")

        if (!appsSubDir.exists()) {
            appsSubDir.mkdir()
        }

        return appsSubDir.toString()
    }

    fun checkIfAppExists(appFeedID: String): Boolean {
        val appsDirectory = File(getAppDirectoryPath())

        val appFolder = File(appsDirectory, appFeedID)

        if (appFolder.exists() && appFolder.isDirectory) {
            return true
        } else {
            return false
        }
    }

    fun listApps(): MutableMap<String, String> {
        val directory = File(getAppDirectoryPath())
        val appsInfo = mutableMapOf<String, String>()

        // Check if the directory exists and is indeed a directory
        if (directory.exists() && directory.isDirectory) {
            // List all files and directories within the directory
            val appFolders = directory.listFiles()

            if (appFolders != null) {
                for (appFolder in appFolders) {
                    if (appFolder.isDirectory) {
                        val iconFile = File(appFolder, "icon.png") //icon always named so
                        val appName = appFolder.name
                        var iconBase64: String

                        if (iconFile.exists()) {
                            try {
                                val fileContent = iconFile.readBytes()
                                iconBase64 = Base64.getEncoder().encodeToString(fileContent)
                            } catch (e: Exception) {
                                iconBase64 = "No Icon"
                            }
                        } else {
                            iconBase64 = "No Icon"
                        }
                        appsInfo[appName] = iconBase64
                    }
                }
            }
        }

        return appsInfo
    }

    fun createDirectory(path: String, folderName: String): Boolean {
        val directory = File(path)
        var status = false

        // Check if the directory exists and is indeed a directory
        if (directory.exists() && directory.isDirectory) {
            val newFolder = File(directory, folderName)
            if (!newFolder.exists()) {
                status = newFolder.mkdir()
            }
        }
        return status
    }

    fun addApp(appName: String, appIcon: String): String {
        val appsDirectory = File(getAppDirectoryPath())

        // Check if app directory exists
        if (appsDirectory.exists() && appsDirectory.isDirectory) {
            val newAppFolder = File(appsDirectory, appName)

            if (!newAppFolder.exists()) {
                val status = newAppFolder.mkdir()
                if (status) {
                    try {
                        val imageBytes = Base64.getDecoder().decode(appIcon)
                        val imageFile = File(newAppFolder, "icon.png")
                        imageFile.writeBytes(imageBytes)
                        return "Successfully added app: $appName"
                    } catch (e: IllegalArgumentException) {
                        // This catches decode errors if the Base64 data is invalid
                        return "Error decoding app icon for: $appName"
                    } catch (e: Exception) {
                        // This catches other errors, such as file write errors
                        return "Error saving app icon for: $appName"
                    }
                } else {
                    return "Error while adding app: " + appName
                }
            } else {
                return "An app exists with the same name"
            }
        } else {
            return "Apps directory does not exist";
        }
    }

    fun removeApp(appName: String): String {
        val appsDirectory = File(getAppDirectoryPath())

        // Check if app directory exists
        if (appsDirectory.exists() && appsDirectory.isDirectory) {
            val appFolder = File(appsDirectory, appName)

            if (appFolder.exists()) {
                appFolder.deleteRecursively()
                if (!appFolder.exists()) {
                    return "Successfully removed app: $appName"
                } else {
                    return "Error while removing app: $appName"
                }
            } else {
                return "No app exists with this name"
            }
        } else {
            return "Apps directory does not exist";
        }
    }

    fun updateApp(appName: String, fileName: String, fileContent: String): String {
        val appsDirectory = File(getAppDirectoryPath())

        // Check if app directory exists
        if (appsDirectory.exists() && appsDirectory.isDirectory) {
            val newAppFolder = File(appsDirectory, appName)

            if (!newAppFolder.exists()) {
                return "No app with name " + appName
            } else {
                try {
                    val fileBytes = Base64.getDecoder().decode(fileContent)
                    val file = File(newAppFolder, fileName)
                    file.writeBytes(fileBytes)
                    return "Successfully updated app: $appName , added file: $fileName"
                } catch (e: IllegalArgumentException) {
                    // This catches decode errors if the Base64 data is invalid
                    return "Error decoding app file for: $appName"
                } catch (e: Exception) {
                    // This catches other errors, such as file write errors
                    return "Error saving app file for: $appName"
                }
                }
        } else {
            return "Apps directory does not exist"
        }
    }

    fun loadApp(appName: String): MutableMap<String, String> {

        val appsDirectory = File(getAppDirectoryPath())
        val appFiles = mutableMapOf<String, String>()

        // Check if the directory exists and is indeed a directory
        if (appsDirectory.exists() && appsDirectory.isDirectory) {
            // List all files and directories within the directory
            val appFolder = File(appsDirectory, appName)

            if (appFolder.exists() && appFolder.isDirectory) {
                val jsFile = File(appFolder, "main.js") //load js file
                val htmlFile = File(appFolder, "main.html") //load html file
                var jsBase64: String
                var htmlBase64: String

                if (jsFile.exists()) {
                    try {
                        val fileContent = jsFile.readBytes()
                        jsBase64 = Base64.getEncoder().encodeToString(fileContent)
                        appFiles["Status"] = "Success"
                        appFiles["JS"] = jsBase64
                    } catch (e: Exception) {
                        appFiles["Status"] = "Error: Could not load JS File for $appName"
                    }
                } else {
                    appFiles["Status"] = "Error: No JS File for $appName"
                }

                if (htmlFile.exists()) {
                    try {
                        val fileContent = htmlFile.readBytes()
                        htmlBase64 = Base64.getEncoder().encodeToString(fileContent)
                        appFiles["Status"] = "Success"
                        appFiles["HTML"] = htmlBase64
                    } catch (e: Exception) {
                        appFiles["Status"] = "Error: Could not load HTML File for $appName"
                    }
                } else {
                    appFiles["Status"] = "Error: No HTML File for $appName"
                }
            }
        } else {
            appFiles["Status"] = "Error: No App with name $appName"
        }
        return appFiles
    }
}