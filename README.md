# WoleetBackupManager
WoleetBackupManager is an automated backup tool for digital data and documents, ensuring integrity, authenticity, and verifiable timestamps through integration with Woleet API.

Features:

Reading parameters from the "settings.yaml" file.
Checking the existence of an anchor ID (anchor_id). If the ID is empty, it means the backup process needs to be executed for the first time. Otherwise, it indicates that the backup has already been performed, and the script needs to check the status of the anchor before continuing.
Creating a backup command for the database using the parameters read from the "settings.yaml" file.
Performing the database backup by executing the backup command.
Hashing the backup file using the SHA256 algorithm to obtain the hashDump.
Renaming the backup file by appending the hashDump to the filename.
Querying the Woleet API to create an anchor by providing the file name and hashDump.
Saving the anchor ID in the "settings.yaml" file.
Waiting for the anchor to complete by periodically checking its status.
Downloading the anchor certificate from Woleet.
Storing the certificate and the backup file in Amazon S3.
How does it work?

Clone the repository: Start by cloning the project repository to obtain the files locally.
Install dependencies: Make sure to install the required dependencies specified in the "requirements.txt" file. You can do this by using the following command: pip install -r requirements.txt. If you're using a Python virtual environment, activate it before performing this step.
Configure settings: Before running the program, ensure that you provide the appropriate values in the "settings.yaml" file. This file contains database connection information, Woleet API and Amazon S3 access credentials, as well as backup paths. Make sure to provide correct values for each parameter.
Run the program: Once the dependencies are installed and the settings are configured, you can run the WoleetBackupManager program. Make sure to use Python 3.8.1 or a compatible version. You can launch the program by executing the command: python woleet_backup_manager.py.
Limitations: If you plan to use WoleetBackupManager in production for recurring scheduled backups, it is recommended to add an additional function to remove the "anchor_id" value from the "settings.yaml" file. Example:

def reset_anchor_id():
    with open('settings.yaml', 'r+') as file:
        config = yaml.safe_load(file)
        if "anchor_id" in config:
            del config["anchor_id"]
        file.seek(0)
        yaml.safe_dump(config, file)
        file.truncate()

