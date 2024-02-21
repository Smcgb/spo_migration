# Sharepoint Migration Script
## Introduction

Our organization faced the challenge of migrating a substantial volume of files from Sharepoint Online to a local drive. After evaluating several costly SaaS solutions, we developed this script as an efficient workaround.
## Configuration

To start, you must create an Azure App Registration to grant the necessary API permissions. These permissions should include:

    Microsoft Graph: Sites.ReadWrite.All (Application level)
    Sharepoint: Sites.ReadWrite.All (Application level)

The script alternates between two API keys after a set number of uses to avoid expiration issues, ensuring continuous access by refreshing tokens upon application restart.

For successful setup, you will need:

    Tenant ID from Azure
    Client ID from your app registration
    Two API keys
    A local file path for the migration (in our case, a directly accessible mounted Azure File Storage)
    Your Sharepoint Tenant and Site names

### Script Limitations

Currently, the script does not delete top-level Sharepoint folders, only files within them. It does, however, remove empty subfolders, leaving behind some empty folders and subfolders in Sharepoint.
Additional Features

The script stores items in a list, allowing for partial processing or reversal for scalable deployment.
Performance Constraints

We observed a download speed limit with our tenant, capping each script instance at 25 gigabytes per hour per run (we are running a forward and reverse version of this script). For smaller data sets, the OneDrive connection tool might be faster. However, for moving over 20 TBs as in our case, this script proved to be a significant time-saver, especially given the frequent corruption issues with large files or batches exceeding 50 files or 10GB in total size when using Sharepoint OneDrive or direct downloads.
