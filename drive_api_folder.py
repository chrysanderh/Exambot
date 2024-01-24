from __future__ import print_function

import os
import logging

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


def get_folder(logger, path, folder_name, parent_folder_id=None):
    """
    Searches for a folder with the given foldername in the shared Google Drive and
    returns the ID of the folder with the desired name

    Parameters
    ----------
    logger : logging.Logger
        Logger object
    path : str
        Path to the folder containing the token.json file.
    folder_name : str
        Name of the folder in shared Google Drive
    parent_folder_id : str, optional
        ID of the parent folder in drive with the desired foldername

    Returns
    -------
    folder_id : str
        ID of the folder in drive with the desired foldername
    """
    SCOPES = ['https://www.googleapis.com/auth/drive']

    creds = Credentials.from_authorized_user_file(os.path.join(path, 'token.json'), SCOPES)

    service = build('drive', 'v3', credentials=creds)

    # List all folders in your Google Drive
    query = f"mimeType='application/vnd.google-apps.folder' and name='{folder_name}'"
    if parent_folder_id is not None:
        query += f" and '{parent_folder_id}' in parents"
    results = service.files().list(
        q=query,
        spaces='drive',
        fields='files(id, name)'
    ).execute()

    for file in results.get("files", []):
        # Process change
        logger.info(f'Found file: {file.get("name")}, {file.get("id")}')

    folders = results.get('files', [])
    folder_id = []
    for folder in folders:
        if folder['name'] == folder_name:
            folder_id.append(folder['id'])
    return folder_id


def clean_data_drive(logger, token_path, folder_id):
    """
    Deletes all files in the folder with the given folder_id

    Parameters
    ----------
    logger : logging.Logger
        Logger object
    token_path : str
        Path to the folder containing the token.json file.
    folder_id : str
        ID of the folder in drive with the desired foldername
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
            logger.info(f"{file['name']} with ID {file['id']} deleted.")

    except HttpError as error:
        logger.error(F'An error occurred: {error}')


def create_folder(logger, path):
    """ 
    Create a folder and prints the folder ID

    Parameters
    ----------
    logger : logging.Logger
        Logger object
    path : str
        Path to the folder containing the token.json file.

    Returns
    -------
    folder_id : str
        ID of the folder in drive with the desired foldername
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
        logger.info(F'Folder ID: "{file.get("id")}".')
        return file.get('id')

    except HttpError as error:
        logger.error(F'An error occurred: {error}')
        return None
