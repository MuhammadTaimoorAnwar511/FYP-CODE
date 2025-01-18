from __future__ import print_function
import os
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# Define the folder ID and file directory
DRIVE_FOLDER_ID = "1KgiZ1JA4TiM6BCJg_lAdykk_aw6MZ_mk"
COMBINED_DIR = "../Data"
FILE_NAMES = [
    "SOL_1d.csv", "SOL_1h.csv", "SOL_4h.csv",
    "PEPE_1d.csv", "PEPE_1h.csv", "PEPE_4h.csv",
    "ETH_1d.csv", "ETH_1h.csv", "ETH_4h.csv",
    "BTC_1d.csv", "BTC_1h.csv", "BTC_4h.csv",
    "BNB_1d.csv", "BNB_1h.csv", "BNB_4h.csv",
]

# Define the scopes and authentication directory
SCOPES = ['https://www.googleapis.com/auth/drive']
TOKEN_DIR = '../Token'

def authenticate():
    """Authenticate and return the Drive API service."""
    creds = None
    # Check for credentials in the 'Token' directory
    if os.path.exists(os.path.join(TOKEN_DIR, 'token.json')):
        creds = Credentials.from_authorized_user_file(os.path.join(TOKEN_DIR, 'token.json'), SCOPES)
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Look for credentials.json in the 'Token' folder
            flow = InstalledAppFlow.from_client_secrets_file(
                os.path.join(TOKEN_DIR, 'credentials.json'), SCOPES)  # Adjusted path for the 'Token' folder
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run in the 'Token' folder
        with open(os.path.join(TOKEN_DIR, 'token.json'), 'w') as token:
            token.write(creds.to_json())
    
    return build('drive', 'v3', credentials=creds)

def list_files_in_folder(service, folder_id):
    """List all files in a specified Google Drive folder."""
    query = f"'{folder_id}' in parents and trashed = false"
    results = service.files().list(q=query).execute()
    return results.get('files', [])

def delete_files_in_folder(service, folder_id):
    """Delete all files in a specified Google Drive folder."""
    files = list_files_in_folder(service, folder_id)
    for file in files:
        service.files().delete(fileId=file['id']).execute()
        print(f"Deleted file: {file['name']} (ID: {file['id']})")

def upload_files_to_folder(service, folder_id, directory, file_names):
    """Upload files to a specified Google Drive folder."""
    for file_name in file_names:
        file_path = os.path.join(directory, file_name)
        if os.path.exists(file_path):
            file_metadata = {'name': file_name, 'parents': [folder_id]}
            media = MediaFileUpload(file_path)
            uploaded_file = service.files().create(
                body=file_metadata, media_body=media, fields='id'
            ).execute()
            print(f"Uploaded file: {file_name} (ID: {uploaded_file['id']})")
        else:
            print(f"File not found: {file_path}")

def main():
    """Main function to delete and upload files to Google Drive."""
    service = authenticate()

    # Step 1: Delete all files in the specified folder
    print("Deleting existing files in the folder...")
    delete_files_in_folder(service, DRIVE_FOLDER_ID)

    # Step 2: Upload new files to the folder
    print("Uploading new files to the folder...")
    upload_files_to_folder(service, DRIVE_FOLDER_ID, COMBINED_DIR, FILE_NAMES)

if __name__ == '__main__':
    main()
