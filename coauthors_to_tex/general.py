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
    This function returns the width of the terminal, there is a default value
    of 80 if the width cannot be determined

    :return: int, the width of the terminal
    """
    terminal_size = shutil.get_terminal_size((80, 20))  # Default to 80 if unable to get size
    return terminal_size.columns


def safe_latex(txt: str) -> str:
    """
    This function replaces the special characters by the latex equivalent

    :param txt:
    :return:
    """
    # This function replaces the special characters by the latex equivalent
    txt = txt.replace(' & ', ' \\& ')
    # We may add some more as we find bugs

    return txt


def latexify_accents(txt: str) -> str:
    """
    This function replaces the accents in the text by the latex equivalent
    :param txt:
    :return: txt with latex accents
    """
    for letter in constants.LETTER_2_LATEX.keys():
        txt = txt.replace(letter, constants.LETTER_2_LATEX[letter])
    return txt


def read_google_sheet_csv(sheet_id: str, gid: str) -> Table:
    """
    This function reads a Google sheet and returns the content as an
    astropy table

    :param sheet_id:
    :param gid:
    :return: the astropy table
    """
    if os.path.exists('.tmp.csv'):
        os.remove('.tmp.csv')

    csv_url = constants.GOOGLE_URL.format(sheet_id=sheet_id, gid=gid)

    _ = wget.download(csv_url, out='.tmp.csv', bar=None)
    tbl = Table.read('.tmp.csv', format='ascii.csv')

    key = tbl.keys()[0]
    tbl = tbl[np.array(tbl[key]) != '']
    tbl = tbl[np.array(tbl[key]) != '0']

    # this is to remove the empty lines in the ORCID column
    if 'ORCID' in tbl.keys():
        orcid = np.array(tbl['ORCID'])
        for i in range(len(orcid)):
            if len(orcid[i]) < 16:
                orcid[i] = ''
        tbl['ORCID'] = orcid

    for key in tbl.keys():
        v = np.char.array(tbl[key])
        # strip the strings for leading and trailing spaces
        v = v.strip(',')
        v = v.strip()
        tbl[key] = v

    # just for sanity, we remove the empty temporary file
    os.remove('.tmp.csv')

    # we remove all columns that have 'COMMENT' in the name
    for key in tbl.keys():
        if 'COMMENT' in key.upper():
            del tbl[key]

    return tbl


def clear():
    """
    This function clears the terminal
    """
    if os.name == 'posix':
        os.system('clear')
    else:
        print('\n' * 50)


def check_columns(tbl, colnames):
    # We check that the table has a set of column names and no other columns
    for col_name in colnames:
        if col_name not in tbl.keys():
            print('~' * get_terminal_width())
            print(f'Error: the table should have a column named *{col_name}*')
            print('Please check the table')
            print('~' * get_terminal_width())
            exit()
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
    This function creates the initials of the authors
    :param first_names:
    :param last_names:
    :return: the initials
    """
    initials = np.zeros(len(first_names), dtype='U100')

    # Remove 'de' or 'da' from the last names if they are there
    for i in range(len(last_names)):
        if last_names[i].lower().startswith('de '):
            last_names[i] = last_names[i][3:]
        if last_names[i].lower().startswith('da '):
            last_names[i] = last_names[i][3:]

    for i in range(len(first_names)):

        # if first name contains a space, then we have to split it
        if ' ' in first_names[i]:
            first_name = first_names[i].split(' ')
            initials[i] = first_name[0][0] + first_name[1][0]
        elif '-' in first_names[i]:
            first_name = first_names[i].split('-')
            initials[i] = first_name[0][0] +'-'+ first_name[1][0]
        else:
            initials[i] = first_names[i][0]

        # if last name contains a space, then we have to split it
        if ' ' in last_names[i]:
            last_name = last_names[i].split(' ')
            initials[i] += last_name[0][0] + last_name[1][0]
        elif '-' in last_names[i]:
            last_name = last_names[i].split('-')
            initials[i] += last_name[0][0] +'-'+ last_name[1][0]
        else:
            initials[i] += last_names[i][0]

    return initials


def main():
    sheet_id = constants.SHEET_ID
    gid0, gid1 = constants.GID0, constants.GID1
    gid2, gid3 = constants.GID2, constants.GID3
    gid4 = constants.GID4
    allowed_paper_styles = constants.ALLOWED_PAPER_STYLES

    # We fetch the data from the google sheet
    print('\nWe fetch the data from the google sheet -- list of papers')
    tbl_papers = read_google_sheet_csv(sheet_id, gid0)
    print('\nWe fetch the data from the google sheet -- list of '
          'affiliations')

    if check_columns(tbl_papers, ['paper key', 'STYLE','ACKNOWLEDGEMENTS', 'author list']):
        print('Columns are correct')
    else:
        exit()

    tbl_affiliations = read_google_sheet_csv(sheet_id, gid1)
    print('\nWe fetch the data from the google sheet -- list of authors '
          '[NIRPS]')

    if check_columns(tbl_affiliations,  ['SHORTNAME', 'AFFILIATION']):
        print('Columns are correct')
    else:
        exit()

    print('\nWe fetch the data from the google sheet -- list of authors ')
    tbl_nirps_authors = read_google_sheet_csv(sheet_id, gid2)

    colnames = ['AUTHOR',
                'Last Name',
                'First Name',
                'ORCID',
                'EMAIL',
                'SHORTNAME',
                'AFFILIATIONS',
                'ACKNOWLEDGEMENTS']

    if check_columns(tbl_nirps_authors, colnames):
        print('Columns are correct')
    else:
        exit()

    print('\nWe fetch the data from the google sheet -- list of authors '
          '[non-NIRPS]')
    if gid3 is not None:
        tbl_nonnirps_authors = read_google_sheet_csv(sheet_id, gid3)

        if check_columns(tbl_nonnirps_authors, colnames):
            print('Columns are correct')
        else:
            exit()


    else:
        tbl_nonnirps_authors = Table()

    print('\nWe fetch the data from the google sheet -- list of acknowledgements')
    tbl_acknowledgements = read_google_sheet_csv(sheet_id, gid4)
    if check_columns(tbl_acknowledgements, ['ACKNOWLEDGEMENTS', 'ACKNOWLEDGEMENTS_TEXT']):
        print('Columns are correct')
    else:
        exit()

    clear()


    duplicate_authors_flag = False
    # We check if authors are duplicated in the two tables
    for i in range(len(tbl_nirps_authors)):
        for j in range(len(tbl_nonnirps_authors)):
            if tbl_nirps_authors['SHORTNAME'][i] == tbl_nonnirps_authors['SHORTNAME'][j]:
                print('~' * get_terminal_width())
                print(
                    f'Error: the author *{tbl_nirps_authors["SHORTNAME"][i]}* is duplicated in the two author lists (NIRPS and non-NIRPS)')
                print('~' * get_terminal_width())
                duplicate_authors_flag = True
    if duplicate_authors_flag:
        exit()

    # We concatenate the two tables of authors, to have a single table
    # with all authors
    tbl_authors = vstack([tbl_nirps_authors, tbl_nonnirps_authors])

    tbl_authors['INITIALS'] = mk_initials(tbl_authors['First Name'], tbl_authors['Last Name'])

    # We have a sanity check to see if the all styles are allowed
    for i in range(len(tbl_papers)):
        if tbl_papers['STYLE'][i].upper() not in allowed_paper_styles:
            print('~' * get_terminal_width())
            print(f'Error: the style *{tbl_papers["STYLE"][i]}* is not allowed')
            print('Please select a style in the list :')
            for style in allowed_paper_styles:
                print(style)
            print('~' * get_terminal_width())
            exit()

    # We ask the user to select the paper for which he wants the
    #    latex author list
    print('Select the paper for which you want the latex author list :')
    for i in range(len(tbl_papers)):
        print('[{}] {}'.format(i + 1, tbl_papers['paper key'][i]))

    # We ask the user to select the paper for which he wants the latex
    #    author list
    ipaper = int(input('Enter the number of the paper : ')) - 1

    # We check if the paper number is in the list
    if ipaper < 0 or ipaper >= len(tbl_papers):
        print('~' * get_terminal_width())
        print(f'Error: the paper number {ipaper + 1} is not in the list')
        print('Please select a number between 1 and {}'.format(len(tbl_papers)))
        print('~' * get_terminal_width())
        exit()

    bad_affil_flag = False
    # We check that all affiliations exist in the list of affiliations
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

    bad_ack = False
    # We check that the acknowledgements are in the list of acknowledgements
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

    # We clear the terminal
    clear()

    # We create a table with the authors of the selected paper
    tbl_authors_paper = Table()
    tbl_authors_paper['SHORTNAME'] = tbl_papers[ipaper]['author list'].split(',')
    tbl_authors_paper['AUTHOR'] = np.zeros(len(tbl_authors_paper), dtype='U100')
    tbl_authors_paper['INITIALS'] = np.zeros(len(tbl_authors_paper), dtype='U100')
    tbl_authors_paper['AFFILIATIONS'] = np.zeros(len(tbl_authors_paper), dtype='U100')
    tbl_authors_paper['ORCID'] = np.zeros(len(tbl_authors_paper), dtype='U100')
    tbl_authors_paper['EMAIL'] = np.zeros(len(tbl_authors_paper), dtype='U100')
    tbl_authors_paper['ACKNOWLEDGEMENTS'] = np.zeros(len(tbl_authors_paper), dtype='U100')

    # We fill the table with the authors information
    for i in range(len(tbl_authors_paper)):
        for j in range(len(tbl_authors)):
            if tbl_authors_paper['SHORTNAME'][i] == tbl_authors['SHORTNAME'][j]:
                tbl_authors_paper['AUTHOR'][i] = tbl_authors['AUTHOR'][j]
                tbl_authors_paper['AFFILIATIONS'][i] = tbl_authors['AFFILIATIONS'][j]
                tbl_authors_paper['ORCID'][i] = tbl_authors['ORCID'][j]
                tbl_authors_paper['EMAIL'][i] = tbl_authors['EMAIL'][j]
                tbl_authors_paper['ACKNOWLEDGEMENTS'][i] = tbl_authors['ACKNOWLEDGEMENTS'][j]
                tbl_authors_paper['INITIALS'][i] = tbl_authors['INITIALS'][j]

    # Sanity checks of the author list
    # First check: are there duplicates in the author list
    for i in range(len(tbl_authors_paper)):
        for j in range(i + 1, len(tbl_authors_paper)):
            if tbl_authors_paper['SHORTNAME'][i] == tbl_authors_paper['SHORTNAME'][j]:
                print('~' * get_terminal_width())
                print(f'Error: the author *{tbl_authors_paper["SHORTNAME"][i]}* is duplicated in the author list')
                print('~' * get_terminal_width())
                exit()
    # Second check: are all the authors in the author list
    for i in range(len(tbl_authors_paper)):
        if tbl_authors_paper['AUTHOR'][i] == '':
            print('~' * get_terminal_width())
            print(f'Error: the author *{tbl_authors_paper["SHORTNAME"][i]}* is not in the author list')
            print('Add to either the NIRPS or non-NIRPS author list')
            print('~' * get_terminal_width())
            exit()

    # We find the style of the paper references
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
                affil_txt += ordered_numerical_tags[affil_str == ordered_affiliations][0]
                if affil_str != author_affiliations[-1]:
                    affil_txt += ','

            if iauthor == 0:  # first author, we add the email
                affil_txt += ',*'

            affil_txt += '}'

            output += author + affil_txt
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
        output += '}\n'

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
            who_txt = ', '.join(who[:-1]) + ' & ' + who[-1] + ' '
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


# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    _ = main()

# =============================================================================
# End of code
# =============================================================================
