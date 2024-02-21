import os
import requests


def get_access_token(tenant_id, client_id, client_secret):
    token_url = f'https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token'
    token_data = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
        'scope': 'https://graph.microsoft.com/.default'
    }
    token_r = requests.post(token_url, data=token_data)
    return token_r.json().get('access_token')

# Function to make a GET request to the specified resource URL
def make_api_call(resource_url, token):
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    response = requests.get(resource_url, headers=headers)
    return response

    #todo cause an error to swap secrets and regen token


# Function to handle pagination and retrieve all items
def get_all_items(items_url, token):
    items = []
    while items_url:
        response = make_api_call(items_url, token)
        response_data = response.json()
        items.extend(response_data.get('value', []))
        items_url = response_data.get('@odata.nextLink', None)
    return items

def get_folder_items(folder, token):
    folder_id = folder.get('id')
    folder_url = f'https://graph.microsoft.com/v1.0/drives/{drive_id}/items/{folder_id}/children'
    folder_items = get_all_items(folder_url, token)
    return folder_items

def download_file(url, local_filename):
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        file_content = r.content
        with open(local_filename, 'wb') as f:
            f.write(file_content)
            print(f'Downloaded {local_filename}')
    return local_filename

def delete_item(drive_id, item_id, token):
    delete_url = f'https://graph.microsoft.com/v1.0/drives/{drive_id}/items/{item_id}'
    headers = {'Authorization': 'Bearer ' + token}
    response = requests.delete(delete_url, headers=headers)
    response.raise_for_status()  # raise an exception if the DELETE request failed

# Function to regenerate token by swapping client secrets
def regenerate_token():
    print("Regenerating token...")
    global client_secret, client_secret2, token
    client_secret, client_secret2 = client_secret2, client_secret
    token = get_access_token(tenant_id, client_id, client_secret)
    print("Token regenerated")

def process_items(items, parent_folder):
    global runs
    for item in items:
        item_path = os.path.join(parent_folder, item.get('name'))
        if runs >= 100:
            regenerate_token()
            runs = 0
        runs += 1
        if item.get('folder'):  # if item is a folder
            os.makedirs(item_path, exist_ok=True)  # create folder
            # get items in the folder
            item_id = item.get('id')
            item_url = f'https://graph.microsoft.com/v1.0/drives/{drive_id}/items/{item_id}/children'
            item_items = get_all_items(item_url, token)
            if item_items:  # process items in the folder only if it has items
                process_items(item_items, item_path)
            else:
                print(f'Folder {item.get("name")} is empty')
                # delete empty folder
                try:
                    delete_item(drive_id, item_id, token)
                except Exception as e:
                    print(f"Error deleting folder {item_id}: {e}")

        elif item.get('file'):  # if item is a file
            # download file
            # delete .bak and .tmp files
            if item.get('name').endswith('.bak') or item.get('name').endswith('.tmp'):
                try:
                    delete_item(drive_id, item['id'], token)
                except Exception as e:
                    print(f"Error deleting file {item['id']}: {e}")
                    continue
            try:
                download_url = item.get('@microsoft.graph.downloadUrl')
                download_file(download_url, item_path)
            except Exception as e:
                print(f'Error downloading {item.get("name")}: {e}')
            try:
                delete_item(drive_id, item['id'], token)
            except Exception as e:
                print(f"Error deleting file {item['id']}: {e}")

# global variables
# secrets, paths and URLs
runs = 0        
tenant_id = 'my_tenet_id'
client_id = 'my_client_id'
client_secret = 'my_secret_key'
client_secret2 = 'my_second_secret_key'
local_path = r"C:\my\local\path\to\download\files\to"
my_tenet = 'my_tenet_name'
my_site = 'my_site_name'
site_resource_url = f'https://graph.microsoft.com/v1.0/sites/{my_tenet}.sharepoint.com:/sites/{my_site}'

token = get_access_token(tenant_id, client_id, client_secret)
# site json response
site_response = make_api_call(site_resource_url, token)
site_id = site_response.json().get('id')

# get the appropriate drive
if site_id:
    drives_url = f'https://graph.microsoft.com/v1.0/sites/{site_id}/drives'
    drives_response = make_api_call(drives_url, token)
    drives = drives_response.json().get('value')

for drive in drives:
    if drive.get('name') == 'Documents':  # Adjust the name if necessary
        drive_id = drive.get('id')
        root_folder_id = 'root'  # Use 'root' to start from the root, or a specific folder ID
        # Handle pagination to retrieve all items
        items_url = f'https://graph.microsoft.com/v1.0/drives/{drive_id}/items/{root_folder_id}/children'
        # this can take several minutes to run, note it only pulls top level items
        print("getting items")
        items = get_all_items(items_url, token)
        print("items length", len(items))
        # Process your items here

# for horizontal scaling, we can use the items list to create a list of folders to process
# reverse the list to process the items in reverse order
# items = items[::-1]

while True:                                 
    try:
        process_items(items, local_path)
    except Exception as e:
        print(f"Error processing items: {e}")
        # regenerate token
        client_secret, client_secret2 = client_secret2, client_secret
        token = get_access_token(tenant_id, client_id, client_secret)
        # restart loop
        continue
    
    # end loop
    break
