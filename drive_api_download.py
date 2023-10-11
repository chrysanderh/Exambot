from __future__ import print_function

import io
import os
from datetime import datetime

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload


def export_excel(path, filename, real_file_id):
    """Download a Document file in PDF format.

    :param real_file_id: ile ID of any workspace document format file
    :param filename:
    :param path:
    Returns : IO object with location
    """

    SCOPES = ['https://www.googleapis.com/auth/drive']

    creds = Credentials.from_authorized_user_file(os.path.join(path, 'token.json'), SCOPES)

    try:
        # create drive api client
        service = build('drive', 'v3', credentials=creds)

        file_id = real_file_id

        # pylint: disable=maybe-no-member
        request = service.files().export_media(fileId=file_id,
                                               mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        file = io.BytesIO()
        downloader = MediaIoBaseDownload(file, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print(F'Download {int(status.progress() * 100)}.')

    except HttpError as error:
        print(F'An error occurred: {error}')
        file = None

    with open(os.path.join(path, filename), 'wb') as output_file:
        output_file.write(file.getvalue())
    print(f'{filename} generated at {path}!')


# if __name__ == '__main__':
#    export_excel(path=r'C:\Users\cdhgn\Documents\ETH Zürich\QEC\Exambot',
#                 filename=f"{datetime.now().year}_{datetime.now().strftime('%m')}_protocols.xlsx",
#                 real_file_id='1AxfeWr3aFOb-QHDkZBvvUaP2NrxmOyBCXfyQ3MqHh4k')

