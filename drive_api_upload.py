from __future__ import print_function
import os
import logging

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload


def upload_basic(logger, token_path, filepath, filename, parents):
    """
    Insert new file from filepath.

    Parameters
    ----------
    logger : logger object
        logger object from the logging module.
    token_path : str
        Path to the folder containing the token.json file.
    filepath : str
        Path to the file to be uploaded.
    filename : str 
        Name of the file to be uploaded.
    parents : list
        List of parent folder IDs.
    """
    SCOPES = ['https://www.googleapis.com/auth/drive']
    creds = Credentials.from_authorized_user_file(os.path.join(token_path, 'token.json'), SCOPES)

    try:
        # create drive api client
        service = build('drive', 'v3', credentials=creds)

        file_metadata = {'name': filename,
                         'parents': parents}
        media = MediaFileUpload(os.path.join(filepath, filename),
                                mimetype='application/pdf')
        # pylint: disable=maybe-no-member
        file = service.files().create(body=file_metadata, media_body=media,
                                      fields='id').execute()
        logger.info(f'{filename} upload successful! File ID: {file.get("id")}')

    except HttpError as error:
        logger.error(F'An error occurred: {error}')
        file = None
