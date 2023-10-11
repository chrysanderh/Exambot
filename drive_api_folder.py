from __future__ import print_function

import os

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


def get_folder(path, folder_name):
    """
    returns the ID of the folder with the desired name
    :param path: path for the token
    :param folder_name: name of the folder in shared Google Drive
    :return: ID of the folder in drive with the desired foldername
    """
    SCOPES = ['https://www.googleapis.com/auth/drive']

    creds = Credentials.from_authorized_user_file(os.path.join(path, 'token.json'), SCOPES)

    service = build('drive', 'v3', credentials=creds)

    # List all folders in your Google Drive
    results = service.files().list(q="mimeType='application/vnd.google-apps.folder'",
                                   spaces='drive',
                                   fields='files(id, name)').execute()

    folders = results.get('files', [])
    folder_id = []
    for folder in folders:
        if folder['name'] == folder_name:
            folder_id.append(folder['id'])
    return folder_id


def clean_data_drive(token_path, folder_id):
    """

    :param token_path:
    :param folder_id:
    :return:
    """
    SCOPES = ['https://www.googleapis.com/auth/drive']
    creds = Credentials.from_authorized_user_file(os.path.join(token_path, 'token.json'), SCOPES)

    try:
        # create drive api client
        service = build('drive', 'v3', credentials=creds)
        # TODO make code better and more failsafe...
        results = service.files().list(q=f"'{folder_id[0]}' in parents",
                                       fields='nextPageToken, files(id, name)').execute()

        files = results.get('files', [])
        for file in files:
            service.files().delete(fileId=file['id']).execute()
            print(f"{file['name']} with ID {file['id']} deleted.")

    except HttpError as error:
        print(F'An error occurred: {error}')


def create_folder(path):
    """ Create a folder and prints the folder ID
    Returns : Folder Id
    """
    SCOPES = ['https://www.googleapis.com/auth/drive']
    creds = Credentials.from_authorized_user_file(os.path.join(path, 'token.json'), SCOPES)

    try:
        # create drive api client
        service = build('drive', 'v3', credentials=creds)
        file_metadata = {
            'name': 'Invoices',
            'mimeType': 'application/vnd.google-apps.folder'
        }

        # pylint: disable=maybe-no-member
        file = service.files().create(body=file_metadata, fields='id'
                                      ).execute()
        print(F'Folder ID: "{file.get("id")}".')
        return file.get('id')

    except HttpError as error:
        print(F'An error occurred: {error}')
        return None


# if __name__ == '__main__':
#    parents = get_folder(r'C:\Users\cdhgn\Documents\ETH Zürich\QEC\Exambot', 'Protocol_PDF')
#    print(parents)
#    clean_folder(r'C:\Users\cdhgn\Documents\ETH Zürich\QEC\Exambot', parents)
