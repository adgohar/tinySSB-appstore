package nz.scuttlebutt.tremolavossbol
import java.io.File
import android.content.Context

class AppsInterface (context: Context) {
    private val context = context

    fun getAppDirectoryPath(): String {
        val appContext = context // Assuming this is called within an Activity or Context
        val filesDir = appContext.filesDir // Path to /data/data/your_app_package_name/files

        // Define the path for the "apps" subdirectory within filesDir
        val appsSubDir = File(filesDir, "apps")

        if (!appsSubDir.exists()) {
            appsSubDir.mkdir()
        }

        return appsSubDir.toString()
    }

    fun listApps(): String {
        val directory = File(getAppDirectoryPath())
        var filesList: String = "Apps: "

        // Check if the directory exists and is indeed a directory
        if (directory.exists() && directory.isDirectory) {
            // List all files and directories within the directory
            val filesAndFolders = directory.listFiles()

            if (filesAndFolders != null) { // Make sure the list is not null
                for (item in filesAndFolders) {
                    if (item.isDirectory) {
                        if (filesList == "Apps: ") {
                            filesList += "${item.name}"
                        } else {
                            filesList += ", ${item.name}"
                        }
                    }
                }
            }
        } else {
            filesList = "The path provided is not a directory or does not exist."
        }

        return filesList
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

    fun addApp(appName: String): String {
        val appsDirectory = File(getAppDirectoryPath())

        // Check if app directory exists
        if (appsDirectory.exists() && appsDirectory.isDirectory) {
            val newAppFolder = File(appsDirectory, appName)

            if (!newAppFolder.exists()) {
                val status = newAppFolder.mkdir()
                if (status) {
                    return "Successfuly added app: " + appName
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
            val newAppFolder = File(appsDirectory, appName)

            if (newAppFolder.exists()) {
                val status = newAppFolder.delete()
                if (status) {
                    return "Successfuly removed app: " + appName
                } else {
                    return "Error while removing app: " + appName
                }
            } else {
                return "No app exists with this name"
            }
        } else {
            return "Apps directory does not exist";
        }
    }

}