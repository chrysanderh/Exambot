import os
import numpy as np
import pandas as pd
import shutil
from datetime import datetime
from pylatex.utils import NoEscape, bold
from pylatex import Document, Command, LargeText, MediumText, LineBreak, NewPage


def clean_data_local(folder_path):
    """
    Empty a local folder before we start adding new data
    :param folder_path:
    :return:
    """
    for file in os.listdir(folder_path):
        os.remove(os.path.join(folder_path, file))
        print(f"{file} deleted.")


def filter_string(text):
    """
    Filters a given string with respect to the UTF-8 charset. Removes emojis etc. that cannot be compiled with LaTeX

    :param text: string input
    :return: filtered string according to UTF-8
    """
    latex = False
    if text.count("$") > 0 and text.count("$") % 2 == 0:
        latex = True
    if not isinstance(text, str):
        return "-"
    filtered_text = ""
    for char in text:
        try:
            char.encode('utf-8')
            filtered_text += char
        except ValueError:
            pass
    return filtered_text, latex


def filter_text(input_text):
    if type(input_text) is list:
        filtered_list = []
        for text in input_text:
            filtered_list.append(filter_string(text))
        return filtered_list
    else:
        filter_string(input_text)


def split_tex(doc, text):
    """
    Takes a summary and splits it in a way that only the latex parts will be included with the NoEscape command

    :param doc:
    :param text:
    :return:
    """
    current_interval = ""
    dollar_count = 0

    for i, char in enumerate(text):
        if char == '$':
            dollar_count += 1
            if dollar_count % 2 == 1:  # One occurrence of '$'
                doc.append(current_interval)
                current_interval = "$"
            else:
                current_interval += "$"
                if i < len(text):
                    if text[i + 1] == " ":      # add space in the same line of the mathmode, if eq is followed by space
                        current_interval += " "
                doc.append(NoEscape(current_interval))
                current_interval = ""
        else:
            current_interval += char
    doc.append(current_interval)  # append final text interval after last $


def create_tex_preamble():
    """
    Creates the LaTeX document with the necessary preamble for the protocols

    :return: pylatex doc with preamble and defined commands
    """
    # Create a new document
    doc = Document()

    # Add packages
    doc.preamble.append(NoEscape(r'\usepackage[svgnames]{xcolor}'))
    doc.preamble.append(NoEscape(r'\usepackage{enumitem}'))
    doc.preamble.append(NoEscape(r'\usepackage{ragged2e}'))
    doc.preamble.append(NoEscape(r'\usepackage[breakable]{tcolorbox}'))
    doc.preamble.append(Command('usepackage', 'graphicx'))
    doc.preamble.append(Command('usepackage', 'geometry', options='left=1in, right=1in, top=1in, bottom=1in'))
    doc.preamble.append(NoEscape(r'\usepackage{eso-pic}'))
    doc.preamble.append(Command('usepackage', 'tikz'))

    # Watermark
    doc.preamble.append(NoEscape(r'\newcommand\Watermark{\put(0, 0.5\paperheight){\parbox[c][\paperheight]{'
                                 r'\paperwidth}{\centering \rotatebox[origin=c]{45}{\tikz\node[opacity=0.1]{'
                                 r'\includegraphics[width=0.7\textwidth]{2023_04_QEC.png}};}}}}'))

    # Colorbox
    doc.preamble.append(NoEscape(r'\newtcolorbox{mycolorbox}{breakable, colback=Gainsboro, coltext=black, '
                                 r'opacityfill=0.15, boxsep=0pt, arc=0pt, boxrule=0pt, left=0pt, right=0pt, top=2pt, '
                                 r'bottom=2pt, nobeforeafter, fontupper=\normalsize, '
                                 r'before upper={\begin{justify}\parindent0pt}, after upper={\end{justify}},}'))
    doc.preamble.append(NoEscape(r'\AddToShipoutPictureBG{\Watermark}'))
    return doc


class DocumentGenerator:
    def __init__(self, path, filename, folder_pdf, folder_tex):
        self.valid_dept = ["itet", "phys", "other"]
        self.folder_path_pdf = os.path.join(path, folder_pdf)
        self.folder_path_tex = os.path.join(path, folder_tex)
        self.full_df = pd.read_excel(os.path.join(path, filename), sheet_name='Sheet2', engine='openpyxl')

    def generate_all_protocols(self):
        """
        generates tex files and compiles to PDF for all subjects and their respective data in a given datasheet
        """
        if not os.path.isdir(self.folder_path_pdf):
            os.mkdir(self.folder_path_pdf)
        if not os.path.isdir(self.folder_path_tex):
            os.mkdir(self.folder_path_tex)
        shutil.copy('2023_04_QEC.png', self.folder_path_pdf)  # need image as watermark in pdf folder
        depts_subjects_df = self.get_valid_subjects(self.full_df)
        for dept, subject in zip(depts_subjects_df['Department'], depts_subjects_df['Subject']):
            subject_df = self.get_subject_data(self.full_df, subject, dept)
            self.make_subject_tex(subject, subject_df)
        os.remove(os.path.join(self.folder_path_pdf, r'2023_04_QEC.png'))  # remove it; we don't want it to be uploaded

    def get_valid_subjects(self, data):
        """
        Get all the valid subjects & depts for a given data input

        :param data: response sheet
        :return: depts_subjects_df: dataframe of all valid subjects along with the associated department
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

        :param data: pandas dataframe with all the responses
        :param subject: subject, e.g. "Quantum Mechanics II"
        :param dept: "itet", "phys", "other"
        :return: df containing all data for a given subject
        """
        depts_subjects_df = self.get_valid_subjects(data)
        valid_depts = depts_subjects_df['Department'].drop_duplicates().to_list()
        valid_subjects = depts_subjects_df['Subject'].drop_duplicates().to_list()
        if dept not in valid_depts:
            raise Exception(f"Invalid dept {dept} entered. Only these keys are valid departments: {valid_depts}.")
        if subject not in valid_subjects:
            raise Exception(f"Invalid dept {subject} entered. Only these keys are valid subjects: {valid_subjects}.")
        index = data[f'Subject_{dept}'] == subject
        subject_df = data[index]
        return subject_df

    def make_subject_tex(self, subject, subject_df):
        """
        Creates a tex file and compiles a PDF for one subject and saves them in respective folders

        :param subject: subject name as a string
        :param subject_df: dataframe containing all the data for one subject
        """
        if subject_df.empty:
            print(f'No data for {subject}, moving on to next one.')
        encoded_semester = {'Fall 2023': '2023B', 'Spring 2023': '2023A', 'Fall 2022': '2022B', 'Spring 2022': '2022A',
                            'Fall 2021': '2021B', 'Spring 2021': '2021A', 'Fall 2020': '2020B', 'Spring 2020': '2020A',
                            'Fall 2019': '2019B'}

        doc = create_tex_preamble()

        # Add document title
        doc.append(NoEscape(r'\begin{center}'))
        doc.append(LargeText(bold(subject)))
        doc.append(LineBreak())
        doc.append(NoEscape(r'\end{center}'))

        # Add content to the document
        for semester in encoded_semester.keys():
            # Create df with subject data for each semester. Skip, if empty
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
                                      f"{datetime.now().year}_{datetime.now().strftime('%m')}_{datetime.now().strftime('%d')}_{subject}"))
        doc.generate_pdf(os.path.join(self.folder_path_pdf,
                                      f"{datetime.now().year}_{datetime.now().strftime('%m')}_{datetime.now().strftime('%d')}_{subject}"),
                         clean_tex=True, compiler='pdflatex')
        print(f'PDF for {subject} generated!')
