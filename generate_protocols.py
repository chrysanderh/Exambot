import os
import shutil
import logging
import numpy as np
import pandas as pd
from datetime import datetime
from pylatex.utils import NoEscape, bold
from pylatex import Document, Command, LargeText, MediumText, LineBreak, NewPage
from protocol_methods import filter_string, split_tex, create_tex_preamble


class DocumentGenerator:
    """
    Class to generate protocols from a given datasheet
    """
    def __init__(self, logger, path, filename, folder_pdf, folder_tex):
        """
        Initialize DocumentGenerator class

        Parameters
        ----------
        logger : logger object
            logger object from the logging module.
        path : str
            Path to the folder containing the token.json file.
        filename : str
            Name of the file containing the protocols.
        folder_pdf : str
            Name of the folder in the shared Google Drive where the PDF protocols should be saved.
        folder_tex : str
            Name of the folder in the shared Google Drive where the LaTeX protocols should be saved.
        """
        self.logger = logger
        self.valid_dept = ["itet", "phys", "other"]
        self.folder_path_pdf = os.path.join(path, folder_pdf)
        self.folder_path_tex = os.path.join(path, folder_tex)
        self.full_df = pd.read_excel(os.path.join(path, filename), sheet_name='Sheet2', engine='openpyxl')

    def generate_all_protocols(self):
        """
        Generates tex files and compiles to PDF for all subjects and their respective data in a given datasheet
        """
        # Create folders if they don't exist
        if not os.path.isdir(self.folder_path_pdf):
            os.mkdir(self.folder_path_pdf)
        if not os.path.isdir(self.folder_path_tex):
            os.mkdir(self.folder_path_tex)
        
        # need image as watermark in pdf folder
        shutil.copy('2023_04_QEC.png', self.folder_path_pdf) 

        # generate protocols for all subjects 
        depts_subjects_df = self.get_valid_subjects(self.full_df)
        for dept, subject in zip(depts_subjects_df['Department'], depts_subjects_df['Subject']):
            subject_df = self.get_subject_data(self.full_df, subject, dept)
            self.make_subject_tex(subject, subject_df)

        # remove image; we don't want it to be uploaded
        os.remove(os.path.join(self.folder_path_pdf, r'2023_04_QEC.png'))  

    def get_valid_subjects(self, data):
        """
        Get all the valid subjects & depts for a given data input.

        Parameters
        ----------
        data : pandas dataframe
            Dataframe containing all the data.

        Returns
        -------
        depts_subjects_df : pandas dataframe
            Dataframe containing all valid subjects and their respective departments.
        """
        depts_subjects_df = pd.DataFrame(columns=['Department', 'Subject'])
        for dept in self.valid_dept:
            dept_subject_df = pd.DataFrame(
                {'Department': [dept] * len(data[f'Subject_{dept}'].dropna().drop_duplicates()),
                 'Subject': data[f'Subject_{dept}'].dropna().drop_duplicates()})
            depts_subjects_df = pd.concat([depts_subjects_df, dept_subject_df], ignore_index=True)
        return depts_subjects_df

    def get_subject_data(self, data, subject, dept):
        """
        Get all text responses for a specific subject from a specific department sorted by semester (latest = pos 0)

        Parameters
        ----------
        data : pandas dataframe
            Dataframe containing all the data.
        subject : str
            Subject name.
        dept : str
            Department name.

        Returns
        -------
        subject_df : pandas dataframe
            Dataframe containing all the data for a given subject.
        """
        depts_subjects_df = self.get_valid_subjects(data)
        valid_depts = depts_subjects_df['Department'].drop_duplicates().to_list()
        valid_subjects = depts_subjects_df['Subject'].drop_duplicates().to_list()

        # check if dept and subject are valid
        if dept not in valid_depts:
            raise Exception(f"Invalid dept {dept} entered. Only these keys are valid departments: {valid_depts}.")
        if subject not in valid_subjects:
            raise Exception(f"Invalid dept {subject} entered. Only these keys are valid subjects: {valid_subjects}.")
        
        # get all data for a given subject
        index = data[f'Subject_{dept}'] == subject
        subject_df = data[index]
        return subject_df

    def make_subject_tex(self, subject, subject_df):
        """
        Creates a tex file and compiles a PDF for one subject and saves them in respective folders

        Parameters
        ----------
        subject : str
            Subject name.
        subject_df : pandas dataframe
            Dataframe containing all the data for a given subject.
        """
        if subject_df.empty:
            self.logger.info(f'No data for {subject}, moving on to next one.')

        # TODO: do a smarter way of encoding semester
        # hardcoded dict to encode semester to LaTeX format
        encoded_semester = {
            'Fall 2025': '2025B', 'Spring 2025': '2025A',
            'Fall 2024': '2024B', 'Spring 2024': '2024A',
            'Fall 2023': '2023B', 'Spring 2023': '2023A', 
            'Fall 2022': '2022B', 'Spring 2022': '2022A',
            'Fall 2021': '2021B', 'Spring 2021': '2021A',
            'Fall 2020': '2020B', 'Spring 2020': '2020A',
            'Fall 2019': '2019B'
        }

        doc = create_tex_preamble()

        # Add document title
        doc.append(NoEscape(r'\begin{center}'))
        doc.append(LargeText(bold(subject)))
        doc.append(LineBreak())
        doc.append(NoEscape(r'\end{center}'))

        # Add content to the document
        for semester in encoded_semester.keys():

            # Create df with subject data for each semester; skip, if empty
            semester_subject_df = subject_df[subject_df['Semester'] == semester]
            if semester_subject_df.empty:
                continue
            examiner = np.sort(semester_subject_df['Examiner'].dropna().unique())[0]

            # Add title for each semester
            doc.append(NoEscape(r'\begin{center}'))
            doc.append(MediumText(bold(f'{semester}, Examiner: {examiner}')))
            doc.append(NoEscape(r'\end{center}'))
            doc.append(NoEscape(r'\begin{enumerate}'))
            for i in range(0, len(semester_subject_df['Summary'])):

                # get filtered string and latex yes/no
                filter_summary, latex = filter_string(semester_subject_df['Summary'].iloc[i])

                # Add grey opaque box around every second entry
                doc.append(NoEscape(r'\item'))
                if i % 2 == 0:
                    doc.append(NoEscape(r'\begin{mycolorbox}'))
                doc.append(bold('Summary:'))
                doc.append(NoEscape(r'\newline'))

                # Add summary and atmosphere to the document
                if latex:
                    split_tex(doc, filter_summary)
                else:
                    doc.append(filter_summary)
                if isinstance(semester_subject_df['Atmosphere'].iloc[i], str):
                    filter_atmosphere, _ = filter_string(semester_subject_df['Atmosphere'].iloc[i])
                    doc.append(NoEscape(r'\newline'))
                    doc.append(NoEscape(r'\newline'))
                    doc.append(bold('Exam atmosphere:'))
                    doc.append(NoEscape(r'\newline'))
                    doc.append(filter_atmosphere)
                
                if i % 2 == 0:
                    doc.append(NoEscape(r'\end{mycolorbox}'))
            doc.append(NoEscape(r'\end{enumerate}'))
            doc.append(NewPage())

        # Generate the LaTeX document and the PDF
        doc.generate_tex(os.path.join(self.folder_path_tex,
                                      f"{datetime.now().year}{datetime.now().strftime('%m')}{datetime.now().strftime('%d')}_{subject}"))
        doc.generate_pdf(os.path.join(self.folder_path_pdf,
                                      f"{datetime.now().year}{datetime.now().strftime('%m')}{datetime.now().strftime('%d')}_{subject}"),
                         clean_tex=True, compiler='pdflatex')
        self.logger.info(f'PDF generated for {subject}.')
