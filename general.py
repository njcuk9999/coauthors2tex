#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Main coauthors 2 text code

Created on 2024-08-13 at 12:50

@author: cook
"""

import os
import shutil

import numpy as np
import wget
from astropy.table import Table, vstack
from coauthors_to_tex import constants

# =============================================================================
# Define variables
# =============================================================================
__version__ = constants.__version__
__date__ = constants.__date__

# =============================================================================
# Define functions
# =============================================================================

def get_terminal_width() -> int:
    """
    Returns the width of the terminal. Defaults to 80 if the width cannot be determined.

    :return: int, the width of the terminal
    """
    terminal_size = shutil.get_terminal_size((80, 20))  # Default to 80 if unable to get size
    return terminal_size.columns


def safe_latex(txt: str) -> str:
    """
    Replaces special characters in a string with their LaTeX equivalents.

    :param txt: Input string
    :return: Modified string with LaTeX-safe characters
    """
    txt = txt.replace(' & ', ' \\& ')  # Replace ampersand with LaTeX-safe version
    return txt


def latexify_accents(txt: str) -> str:
    """
    Replaces accented characters in a string with their LaTeX equivalents.

    :param txt: Input string
    :return: Modified string with LaTeX-safe accents
    """
    for letter in constants.LETTER_2_LATEX.keys():
        txt = txt.replace(letter, constants.LETTER_2_LATEX[letter])
    return txt


def read_google_sheet_csv(sheet_id: str, gid: str) -> Table:
    """
    Reads a Google Sheet as a CSV file and returns its content as an Astropy Table.

    :param sheet_id: Google Sheet ID
    :param gid: Google Sheet GID (tab identifier)
    :return: Astropy Table containing the sheet data
    """
    # Remove temporary file if it exists
    if os.path.exists('.tmp.csv'):
        os.remove('.tmp.csv')

    # Construct the URL for the Google Sheet
    csv_url = constants.GOOGLE_URL.format(sheet_id=sheet_id, gid=gid)

    # Download the CSV file
    _ = wget.download(csv_url, out='.tmp.csv', bar=None)
    tbl = Table.read('.tmp.csv', format='ascii.csv')

    # Remove empty or invalid rows
    key = tbl.keys()[0]
    tbl = tbl[np.array(tbl[key]) != '']
    tbl = tbl[np.array(tbl[key]) != '0']

    # Clean up ORCID column
    if 'ORCID' in tbl.keys():
        orcid = np.array(tbl['ORCID'])
        for i in range(len(orcid)):
            if len(orcid[i]) < 16:
                orcid[i] = ''
        tbl['ORCID'] = orcid

    # Strip leading/trailing spaces from all columns
    for key in tbl.keys():
        v = np.char.array(tbl[key])
        v = v.strip(',')
        v = v.strip()
        tbl[key] = v

    # Remove temporary file
    os.remove('.tmp.csv')

    # Remove columns containing 'COMMENT' in their name
    for key in tbl.keys():
        if 'COMMENT' in key.upper():
            del tbl[key]

    return tbl


def clear():
    """
    Clears the terminal screen.
    """
    if os.name == 'posix':  # For Unix-based systems
        os.system('clear')
    else:  # For other systems
        print('\n' * 50)


def check_columns(tbl, colnames):
    """
    Validates that a table contains the required columns and no extra columns.

    :param tbl: Input table
    :param colnames: List of required column names
    :return: True if validation passes, exits otherwise
    """
    # Check for missing required columns
    for col_name in colnames:
        if col_name not in tbl.keys():
            print('~' * get_terminal_width())
            print(f'Error: the table should have a column named *{col_name}*')
            print('Please check the table')
            print('~' * get_terminal_width())
            exit()

    # Check for extra columns
    for col_name in tbl.keys():
        if col_name not in colnames:
            print('~' * get_terminal_width())
            print(f'Error: the table should not have a column named *{col_name}*')
            print('Please check the table')
            print('~' * get_terminal_width())
            exit()

    return True


def mk_initials(first_names, last_names):
    """
    Generates unique initials for authors based on their first and last names.

    :param first_names: List of first names
    :param last_names: List of last names
    :return: List of unique initials
    """
    initials = np.zeros(len(first_names), dtype='U100')
    Nlast = np.ones(len(last_names), dtype=int)  # Number of letters to use from last name
    duplicate = np.ones(len(last_names), dtype=bool)  # Track duplicates
    Nite = 0  # Iteration counter

    while True in duplicate:
        # Remove prefixes like 'de' or 'da' from last names
        for i in range(len(last_names)):
            if last_names[i].lower().startswith('de '):
                last_names[i] = last_names[i][3:]
            if last_names[i].lower().startswith('da '):
                last_names[i] = last_names[i][3:]

        # Generate initials
        for i in range(len(first_names)):
            if ' ' in first_names[i]:  # Handle compound first names
                first_name = first_names[i].split(' ')
                initials[i] = first_name[0][0] + first_name[1][0]
            elif '-' in first_names[i]:  # Handle hyphenated first names
                first_name = first_names[i].split('-')
                initials[i] = first_name[0][0] + '-' + first_name[1][0]
            else:
                initials[i] = first_names[i][0]

            if ' ' in last_names[i]:  # Handle compound last names
                last_name = last_names[i].split(' ')
                initials[i] += last_name[0][0:Nlast[i]] + last_name[1][0:Nlast[i]]
            elif '-' in last_names[i]:  # Handle hyphenated last names
                last_name = last_names[i].split('-')
                initials[i] += last_name[0][0:Nlast[i]] + '-' + last_name[1][0:Nlast[i]]
            else:
                initials[i] += last_names[i][0:Nlast[i]]

        # Check for duplicates
        duplicate = np.zeros(len(initials), dtype=bool)
        for i in range(len(initials)):
            for j in range(i + 1, len(initials)):
                if initials[i] == initials[j]:
                    duplicate[i] = True
                    duplicate[j] = True

        Nlast[duplicate] += 1  # Increase the number of letters used for duplicates
        Nite += 1
        if Nite > 10:  # Prevent infinite loops
            print('~' * get_terminal_width())
            print('Error: too many iterations to find unique initials')
            print('Please check the list of authors')
            print('We keep having problems finding unique initials')
            print('of coauthors {}'.format('+'.join(initials[duplicate])))
            print('~' * get_terminal_width())
            exit()

    return initials



def main():
    # Retrieve constants for Google Sheet IDs and allowed paper styles
    sheet_id = constants.SHEET_ID
    gid0, gid1 = constants.GID0, constants.GID1
    gid2, gid3 = constants.GID2, constants.GID3
    gid4 = constants.GID4
    allowed_paper_styles = constants.ALLOWED_PAPER_STYLES

    # Fetch the list of papers from the Google Sheet
    print('\nWe fetch the data from the google sheet -- list of papers')
    tbl_papers = read_google_sheet_csv(sheet_id, gid0)

    # Fetch the list of affiliations from the Google Sheet
    print('\nWe fetch the data from the google sheet -- list of affiliations')
    if check_columns(tbl_papers, ['paper key', 'STYLE', 'ACKNOWLEDGEMENTS', 'author list']):
        print('Columns are correct')
    else:
        exit()

    tbl_affiliations = read_google_sheet_csv(sheet_id, gid1)

    # Fetch the list of NIRPS authors from the Google Sheet
    print('\nWe fetch the data from the google sheet -- list of authors [NIRPS]')
    if check_columns(tbl_affiliations, ['SHORTNAME', 'AFFILIATION']):
        print('Columns are correct')
    else:
        exit()

    print('\nWe fetch the data from the google sheet -- list of authors ')
    tbl_nirps_authors = read_google_sheet_csv(sheet_id, gid2)

    # Define the required column names for authors
    colnames = ['AUTHOR',
                'Last Name',
                'First Name',
                'ORCID',
                'EMAIL',
                'SHORTNAME',
                'AFFILIATIONS',
                'ACKNOWLEDGEMENTS']

    # Check if the NIRPS authors table has the required columns
    if check_columns(tbl_nirps_authors, colnames):
        print('Columns are correct')
    else:
        exit()

    # Fetch the list of non-NIRPS authors from the Google Sheet
    print('\nWe fetch the data from the google sheet -- list of authors [non-NIRPS]')
    if gid3 is not None:
        tbl_nonnirps_authors = read_google_sheet_csv(sheet_id, gid3)

        if check_columns(tbl_nonnirps_authors, colnames):
            print('Columns are correct')
        else:
            exit()
    else:
        # If no non-NIRPS authors, create an empty table
        tbl_nonnirps_authors = Table()

    # Fetch the list of acknowledgements from the Google Sheet
    print('\nWe fetch the data from the google sheet -- list of acknowledgements')
    tbl_acknowledgements = read_google_sheet_csv(sheet_id, gid4)
    if check_columns(tbl_acknowledgements, ['ACKNOWLEDGEMENTS', 'ACKNOWLEDGEMENTS_TEXT']):
        print('Columns are correct')
    else:
        exit()

    # Clear the terminal screen
    clear()

    # Check for duplicate authors between NIRPS and non-NIRPS lists
    duplicate_authors_flag = False
    for i in range(len(tbl_nirps_authors)):
        for j in range(len(tbl_nonnirps_authors)):
            if tbl_nirps_authors['SHORTNAME'][i] == tbl_nonnirps_authors['SHORTNAME'][j]:
                print('~' * get_terminal_width())
                print(f'Error: the author *{tbl_nirps_authors["SHORTNAME"][i]}* is duplicated in the two author lists (NIRPS and non-NIRPS)')
                print('~' * get_terminal_width())
                duplicate_authors_flag = True
    if duplicate_authors_flag:
        exit()

    # Combine NIRPS and non-NIRPS authors into a single table
    tbl_authors = vstack([tbl_nirps_authors, tbl_nonnirps_authors])

    # Validate that all paper styles are allowed
    for i in range(len(tbl_papers)):
        if tbl_papers['STYLE'][i].upper() not in allowed_paper_styles:
            print('~' * get_terminal_width())
            print(f'Error: the style *{tbl_papers["STYLE"][i]}* is not allowed')
            print('Please select a style in the list :')
            for style in allowed_paper_styles:
                print(style)
            print('~' * get_terminal_width())
            exit()

    # Check that all authors in the papers exist in the authors list
    bad_author_flag = False
    for i in range(len(tbl_papers)):
        authors = tbl_papers['author list'][i].split(',')
        for author in authors:
            if author == '':
                print(f'There is an empty author in the author list of paper: {tbl_papers["paper key"][i]}')
                print('Please remove the empty author')
                continue
            if author not in tbl_authors['SHORTNAME']:
                print('~' * get_terminal_width())
                print(f'There is a problem in the co-author list of paper: {tbl_papers["paper key"][i]}')
                print(f'Error: the author *{author}* is not in the list of authors')
                print('Please add the author to the list of authors')
                print('~' * get_terminal_width())
                bad_author_flag = True
    if bad_author_flag:
        exit()

    # Check for duplicate SHORTNAME entries in the authors table
    flag_double = False
    for i in range(len(tbl_authors)):
        for j in range(i + 1, len(tbl_authors)):
            if tbl_authors['SHORTNAME'][i] == tbl_authors['SHORTNAME'][j]:
                print('~' * get_terminal_width())
                print(f'Error: the author *{tbl_authors["SHORTNAME"][i]}* is duplicated in the author list')
                print('~' * get_terminal_width())
                flag_double = True
    if flag_double:
        exit()

    # Process acknowledgements to add LaTeX hyperlinks for URLs
    for i in range(len(tbl_acknowledgements)):
        ack = tbl_acknowledgements['ACKNOWLEDGEMENTS_TEXT'][i]
        if 'http' in ack:
            ack = ack.split(' ')
            for j in range(len(ack)):
                if 'http' in ack[j]:
                    ack_text = (ack[j].split('://'))[-1]
                    ack_link = ack[j]
                    # Remove trailing characters like '.' or 'doi.org/'
                    trimmed_char = ['doi.org/', '.']
                    for c in trimmed_char:
                        if ack_link.endswith(c):
                            ack_link = ack_link[:-1]
                        if ack_text.startswith(c):
                            ack_text = ack_text[len(c):]
                    ack[j] = '\\href{' + ack_link + '}{' + ack_text + '}'
            tbl_acknowledgements['ACKNOWLEDGEMENTS_TEXT'][i] = ' '.join(ack)

    # Prompt the user to select a paper for generating the LaTeX author list
    print('Select the paper for which you want the latex author list:')
    for i in range(len(tbl_papers)):
        print(f'[{i + 1}] {tbl_papers["paper key"][i]}')

    # Get the user's selection and validate it
    ipaper = int(input('Enter the number of the paper: ')) - 1
    if ipaper < 0 or ipaper >= len(tbl_papers):
        print('~' * get_terminal_width())
        print(f'Error: the paper number {ipaper + 1} is not in the list')
        print(f'Please select a number between 1 and {len(tbl_papers)}')
        print('~' * get_terminal_width())
        exit()

    # Check that all affiliations in the authors table exist in the affiliations list
    bad_affil_flag = False
    for i in range(len(tbl_authors)):
        affil_author = (tbl_authors['AFFILIATIONS'][i].replace(' ', '')).split(',')
        for affil in affil_author:
            if affil not in tbl_affiliations['SHORTNAME']:
                print('~' * get_terminal_width())
                print(f'Error: the affiliation *{affil}* is not in the list of affiliations')
                print(f'This is a problem for author: {tbl_authors["AUTHOR"][i]}')
                print('Please add the affiliation to the list of affiliations')
                print('~' * get_terminal_width())
                bad_affil_flag = True
    if bad_affil_flag:
        exit()

    # Check that all acknowledgements in the authors table exist in the acknowledgements list
    bad_ack = False
    for i in range(len(tbl_authors)):
        ack_author = (tbl_authors['ACKNOWLEDGEMENTS'][i].replace(' ', '')).split(',')
        if ack_author == ['0']:
            continue
        for ack in ack_author:
            if ack not in tbl_acknowledgements['ACKNOWLEDGEMENTS']:
                print('~' * get_terminal_width())
                print(f'Error: the acknowledgement *{ack}* is not in the list of acknowledgements')
                print(f'This is a problem for author: {tbl_authors["AUTHOR"][i]}')
                print('Please add the acknowledgement to the list of acknowledgements')
                print('~' * get_terminal_width())
                bad_ack = True
    if bad_ack:
        exit()

    # Clear the terminal screen again
    clear()

    # Create a table for the authors of the selected paper
    tbl_authors_paper = Table(names=tbl_authors.colnames,
                              dtype=[tbl_authors[col].dtype for col in tbl_authors.colnames])

    # Populate the authors table for the selected paper
    authors_paper = np.array(tbl_papers[ipaper]['author list'].split(','))
    for j in range(len(authors_paper)):
        for i in range(len(tbl_authors)):
            if authors_paper[j] == tbl_authors['SHORTNAME'][i]:
                tbl_authors_paper.add_row(tbl_authors[i])

    # Generate initials for the authors of the selected paper
    tbl_authors_paper['INITIALS'] = mk_initials(tbl_authors_paper['First Name'], tbl_authors_paper['Last Name'])

    # Perform sanity checks on the author list
    # Check for duplicate authors in the selected paper's author list
    for i in range(len(tbl_authors_paper)):
        for j in range(i + 1, len(tbl_authors_paper)):
            if tbl_authors_paper['SHORTNAME'][i] == tbl_authors_paper['SHORTNAME'][j]:
                print('~' * get_terminal_width())
                print(f'Error: the author *{tbl_authors_paper["SHORTNAME"][i]}* is duplicated in the author list')
                print('~' * get_terminal_width())
                exit()

    # Check for missing authors in the selected paper's author list
    for i in range(len(tbl_authors_paper)):
        if tbl_authors_paper['AUTHOR'][i] == '':
            print('~' * get_terminal_width())
            print(f'Error: the author *{tbl_authors_paper["SHORTNAME"][i]}* is not in the author list')
            print('Add to either the NIRPS or non-NIRPS author list')
            print('~' * get_terminal_width())
            exit()

    # Determine the style of the paper (e.g., AJ or A&A) and generate LaTeX output
    paper_style = tbl_papers[ipaper]['STYLE'].upper()

    # We create the latex output for the Astronomical Journal style
    if paper_style == 'AJ':
        output = ''
        for iauthor in range(len(tbl_authors_paper)):
            author = tbl_authors_paper['AUTHOR'][iauthor]
            orcid = tbl_authors_paper['ORCID'][iauthor]
            if len(orcid) > 4:
                orcid = '[' + orcid + ']'
            else:
                orcid = ''

            output += '\\author' + orcid + '{' + author + '}\n'

            author_affiliations = tbl_authors_paper['AFFILIATIONS'][iauthor].split(',')

            for affil in author_affiliations:
                g = tbl_affiliations['SHORTNAME'] == affil
                affiliation = tbl_affiliations[g]['AFFILIATION'][0]
                output += '\\affiliation{' + affiliation + '}\n'

            output += '\n'

    # We create the latex output for the Astronomy and Astrophysics style
    elif paper_style == 'AANDA':
        # loop through authors to find affliations in order
        ordered_affiliations = []
        ordered_numerical_tags = []
        for affil in tbl_authors_paper['AFFILIATIONS']:
            for a in affil.split(','):
                a_str = a.strip()
                if a_str not in ordered_affiliations:
                    ordered_affiliations.append(a_str)
                    ordered_numerical_tags.append(str(len(ordered_affiliations)))

        ordered_affiliations = np.array(ordered_affiliations)
        ordered_numerical_tags = np.array(ordered_numerical_tags)

        output = ''

        output += '\\author{\n'
        for iauthor in range(len(tbl_authors_paper)):
            author = tbl_authors_paper['AUTHOR'][iauthor]

            author_affiliations = tbl_authors_paper['AFFILIATIONS'][iauthor].split(',')

            affil_txt = '\\inst{'

            for affil in author_affiliations:
                affil_str = affil.strip()
                # ordered_numerical_tags[affil == ordered_affiliations][0]
                valid = np.where(affil == ordered_affiliations)[0]
                print(affil_str,valid)
                affil_txt += ordered_numerical_tags[affil_str == ordered_affiliations][0]
                if affil_str != author_affiliations[-1]:
                    affil_txt += ','

            if iauthor == 0:  # first author, we add the email
                affil_txt += ',*'

            affil_txt += '}'



            output += author + affil_txt

            orcid = tbl_authors_paper['ORCID'][iauthor]

            if len(orcid) > 4:
                orcid = '\orcidlink{' + orcid + '}'
                output += orcid

            if iauthor != len(tbl_authors_paper) - 1:
                output += ',\n'
            else:
                output += '\n'



        output += '}\n'
        output += '\n'

        output += '\\institute{\n'
        for iaffil in range(len(ordered_affiliations)):
            affiliation_text = tbl_affiliations['AFFILIATION'][tbl_affiliations['SHORTNAME'] == ordered_affiliations[
                iaffil]][0]
            output += '\\inst{' + ordered_numerical_tags[iaffil] + '}' + affiliation_text + '\\\\\n'
        output += '\inst{*}\\email{' + tbl_authors_paper['EMAIL'][0] + '}\n'
        output += '}'


        output += '\n'

    else:
        raise ValueError(f'The style {paper_style} is not implemented')

    output = latexify_accents(output)
    output = safe_latex(output)

    # We print the latex output
    print('~' * get_terminal_width())
    print(output)
    print('~' * get_terminal_width())
    print('\tCo-author list for arXiv submission')
    print('~' * get_terminal_width())
    print(latexify_accents(', '.join(tbl_authors_paper['AUTHOR'])))


    ackoutput = ''

    ack_paper = tbl_papers[ipaper]['ACKNOWLEDGEMENTS']
    for ack in ack_paper.replace(' ','').split(','):
        if ack == '0':
            continue
        g_ack = tbl_acknowledgements['ACKNOWLEDGEMENTS'] == ack

        if np.sum(g_ack) == 0:
            print('*'*get_terminal_width())
            print('\n')
            print('\tError with the acknowledgement {}'.format(ack))
            print('\tThe acknowledgement is not in the google sheet')
            print('\tPlease fix the acknowledgement in the google sheet')
            print('\n')
            print('*'*get_terminal_width())

            exit()


        tmp = tbl_acknowledgements['ACKNOWLEDGEMENTS_TEXT'][g_ack].data[0]
        if '{INITIALS}' in tmp:

            print('*'*get_terminal_width())
            print('\n')
            print('\tError with the acknowledgement {}'.format(ack))
            print('\tThe text of the acknowledgement contains {INITIALS}')
            print('\t but it is used for the entire paper. This is not allowed')
            print('\tYou should attribute the acknowledgement to authors')
            print('\tPlease fix the acknowledgement in the google sheet')
            print('\n')
            print('*'*get_terminal_width())

            exit()
        ackoutput += tmp + '\\\\\n'

    # we find all the unique acknowledgements
    unique_acknowledgements = []
    for ack in tbl_authors_paper['ACKNOWLEDGEMENTS']:
        ack2 = ack.replace(' ','').split(',')
        for aa in ack2:
            if aa == '0':
                continue
            if aa not in unique_acknowledgements:
                unique_acknowledgements.append(aa)




    for iuack, uack in enumerate(unique_acknowledgements):
        who = []
        for in_ack in range(len(tbl_authors_paper)):
            if uack in tbl_authors_paper['ACKNOWLEDGEMENTS'][in_ack]:
                who.append(tbl_authors_paper['INITIALS'][in_ack])

        # We join with a come except the last one that has an &
        if len(who) > 1:
            who_txt = ', '.join(who[:-1]) + ' \\& ' + who[-1] + ' '
        else:
            who_txt = who[0] + ' '

        g_ack = tbl_acknowledgements['ACKNOWLEDGEMENTS'] == uack
        txt_ack =  tbl_acknowledgements['ACKNOWLEDGEMENTS_TEXT'][g_ack].data[0]
        if '{INITIALS}' in txt_ack:
            txt_ack = txt_ack.replace('{INITIALS}', who_txt)


        ackoutput += txt_ack
        if iuack != len(unique_acknowledgements) - 1:
            ackoutput += '\\\\\n'

    ackoutput = latexify_accents(ackoutput)

    print('~' * get_terminal_width())
    print('\tAcknowledgements ')
    print('~' * get_terminal_width())
    print(ackoutput)
    print('~' * get_terminal_width())

    output = output + '\n\n' + ackoutput


    while '  ' in output:
        output = output.replace('  ', ' ')  # remove double spaces

    # output to a file called tbl_papers['paper key'][i]+'_coauthors.tex'
    with open(tbl_papers[ipaper]['paper key'] + '_coauthors.tex', 'w') as f:
        f.write(output)

    print('~' * get_terminal_width())
    print('\t co-author emails')

    for i in range(len(tbl_authors_paper)):
        email = str(tbl_authors_paper['EMAIL'][i]).strip(' ')
        if email == '0':
            tbl_authors_paper['EMAIL'][i] = '[' + tbl_authors_paper['AUTHOR'][i]+']'

    print(', '.join(tbl_authors_paper['EMAIL']))
    print('~' * get_terminal_width())

# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    _ = main()

# =============================================================================
# End of code
# =============================================================================
