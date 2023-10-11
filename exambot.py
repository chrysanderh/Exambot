from __future__ import print_function

import io
import os
import logging
from datetime import datetime

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload
from drive_api_download import export_excel
from generate_protocols import DocumentGenerator, clean_data_local
from drive_api_upload import upload_basic
from drive_api_folder import get_folder, clean_data_drive


# TODO: logger and ini files for full task automation
logging.basicConfig(filename=f"{datetime.now().year}_{datetime.now().strftime('%m')}_{datetime.now().strftime('%d')}_log.txt",
                    filemode='w',
                    format='%(asctime)s: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.INFO)


def exambot(path, protocols_filename, folder_pdf='Protocol_PDF', folder_tex='Protocol_Latex'):
    export_excel(path=path,
                 filename=protocols_filename,
                 real_file_id='1AxfeWr3aFOb-QHDkZBvvUaP2NrxmOyBCXfyQ3MqHh4k')  # get sheet from drive
    logging.info(f"{protocols_filename} downloaded. Saved at {path}.")
    pdf_gen = DocumentGenerator(path, protocols_filename, folder_pdf, folder_tex)  # create instance
    clean_data_local(pdf_gen.folder_path_pdf)                   # remove all PDFs
    clean_data_local(pdf_gen.folder_path_tex)                   # remove all Tex files
    pdf_gen.generate_all_protocols()                            # generate all protocols
    folder_id = get_folder(path=path, folder_name=folder_pdf)   # get drive folder ID
    clean_data_drive(path, folder_id)                           # delete all files in respective drive folder
    for file in os.listdir(pdf_gen.folder_path_pdf):
        upload_basic(path, pdf_gen.folder_path_pdf, file, folder_id)


if __name__ == '__main__':
    # TODO replace with your filepath
    path = 'C:/Users/cdhgn/Documents/ETH Zürich/QEC/Exambot'
    protocols_filename = f"{datetime.now().year}_{datetime.now().strftime('%m')}_{datetime.now().strftime('%d')}_protocols.xlsx"
    exambot(path=path, protocols_filename=protocols_filename)
