import os
import shutil
import logging
from datetime import datetime
from pylatex.utils import NoEscape, bold
from pylatex import Document, Command, LargeText, MediumText, LineBreak, NewPage


def clean_data_local(logger, folder_path):
    """
    Empty a local folder before we start adding new data

    Parameters
    ----------
    folder_path : str
        Path to the folder that should be emptied.
    """
    for file in os.listdir(folder_path):
        os.remove(os.path.join(folder_path, file))
        logger.info(f"Deleted {file}")
    logger.info(f"Cleaned local folder {folder_path} ")

def filter_string(text):
    """
    Filters a given string with respect to the UTF-8 charset. Removes emojis etc. that cannot be compiled with LaTeX

    Parameters
    ----------
    text : str
        String that should be filtered.

    Returns
    -------
    filtered_text : str
        Filtered string according to UTF-8.
    latex : bool
        True, if the string contains LaTeX code.
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

    Parameters
    ----------
    doc : pylatex document
        pylatex document to which the text should be added
    text : str
        String that should be split and added to the document
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

    Returns
    -------
    doc : pylatex document
        pylatex document with preamble and defined commands
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
    doc.preamble.append(NoEscape(
        r'\newcommand\Watermark{\put(0, 0.5\paperheight){\parbox[c][\paperheight]{'
        r'\paperwidth}{\centering \rotatebox[origin=c]{45}{\tikz\node[opacity=0.1]{'
        r'\includegraphics[width=0.7\textwidth]{2023_04_QEC.png}};}}}}')
    )

    # Colorbox
    doc.preamble.append(NoEscape(
        r'\newtcolorbox{mycolorbox}{breakable, colback=Gainsboro, coltext=black, '
        r'opacityfill=0.15, boxsep=0pt, arc=0pt, boxrule=0pt, left=0pt, right=0pt, top=2pt, '
        r'bottom=2pt, nobeforeafter, fontupper=\normalsize, '
        r'before upper={\begin{justify}\parindent0pt}, after upper={\end{justify}},}')
    )
    doc.preamble.append(NoEscape(r'\AddToShipoutPictureBG{\Watermark}'))
    return doc