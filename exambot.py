from __future__ import print_function

import io
import os
import glob
import logging
import configparser
from datetime import datetime

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload
from drive_api_download import export_excel
from generate_protocols import DocumentGenerator
from protocol_methods import clean_data_local
from drive_api_upload import upload_basic
from drive_api_folder import get_folder, clean_data_drive

# Initialize the ConfigParser
config = configparser.ConfigParser()

# Read the ini file
config.read('exambot.ini')

# Access the values
excel_ID = config['google_ID']['spreadsheet_ID']
parent_folder_ID = config['google_ID']['parent_folder_ID']
filepath = config['filepath']['filepath_local']


# delete old log files
full_path = os.path.join(filepath, '*.txt')
files_to_delete = glob.glob(full_path)

# Iterate over the list of files and delete each one
for file_path in files_to_delete:
    try:
        os.remove(file_path)
        print(f'Successfully deleted: {file_path}')
    except Exception as e:
        print(f'Error while deleting file: {file_path}. Reason: {e}')


# Initialize logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)  # Set the logging level

# Create handlers
log_filename = f"{datetime.now().year}{datetime.now().strftime('%m')}{datetime.now().strftime('%d')}_log.txt"
file_handler = logging.FileHandler(log_filename, mode='w')
console_handler = logging.StreamHandler()

# Create formatters and add it to the handlers
log_format = logging.Formatter('%(asctime)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
file_handler.setFormatter(log_format)
console_handler.setFormatter(log_format)

# Add handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)


def exambot(path, protocols_filename, folder_pdf='Protocol_PDF', folder_tex='Protocol_Latex'):
    """
    Executes all functions needed to generate protocols from the data in the shared Google Drive.

    Parameters
    ----------
    path : str
        Path to the folder containing the token.json file.
    protocols_filename : str
        Name of the file containing the protocols.
    folder_pdf : str
        Name of the folder in the shared Google Drive where the PDF protocols should be saved.
    folder_tex : str
        Name of the folder in the shared Google Drive where the LaTeX protocols should be saved.
    """

    # Delete old protocol spreadsheets
    full_path = os.path.join(path, '*.xlsx')
    files_to_delete = glob.glob(full_path)

    # Iterate over the list of files and delete each one
    for file_path in files_to_delete:
        try:
            os.remove(file_path)
            logger.info(f'Successfully deleted: {file_path}')
        except Exception as e:
            logger.error(f'Error while deleting file: {file_path}. Reason: {e}')

    # get sheet from drive
    export_excel(
        logger,
        path=path,
        filename=protocols_filename,
        real_file_id=excel_ID
    )
    logger.info(f"{protocols_filename} downloaded. Saved at {path}.")

    # create instance of DocumentGenerator
    pdf_gen = DocumentGenerator(logger, path, protocols_filename, folder_pdf, folder_tex)  
    
    # clean data
    clean_data_local(logger, pdf_gen.folder_path_pdf)
    clean_data_local(logger, pdf_gen.folder_path_tex)
    logger.info(f"Data cleaned.")

    # generate all protocols
    pdf_gen.generate_all_protocols()
    logger.info(f"Protocols generated.")
    
    # delete all files in respective drive folder
    folder_id = get_folder(logger, path=path, folder_name=folder_pdf, parent_folder_id=parent_folder_ID)
    clean_data_drive(logger, path, folder_id)
    logger.info(f"Old PDF protocols deleted.")
    for file in os.listdir(pdf_gen.folder_path_pdf):
        upload_basic(logger, path, pdf_gen.folder_path_pdf, file, folder_id)
    logger.info(f"PDF protocols uploaded.")


if __name__ == '__main__':
    path = filepath
    protocols_filename = f"{datetime.now().year}{datetime.now().strftime('%m')}{datetime.now().strftime('%d')}_protocols.xlsx"
    exambot(path=path, protocols_filename=protocols_filename)
