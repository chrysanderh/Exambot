from __future__ import print_function
import os

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload


def upload_basic(token_path, filepath, filename, parents):
    # TODO finish docstring
    """
    Insert new file from filepath.
    :param token_path:
    :param filepath:
    :param filename:
    :param parents:
    :return:
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
        print(f'{filename} upload successful! File ID: {file.get("id")}')

    except HttpError as error:
        print(F'An error occurred: {error}')
        file = None


# if __name__ == '__main__':
#    upload_basic(token_path=r'C:\Users\cdhgn\Documents\ETH Zürich\QEC\Exambot')
