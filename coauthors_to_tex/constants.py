#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2024-08-30 at 12:16

@author: cook
"""
# =============================================================================
# Define variables
# =============================================================================
__version__ = '1.6'
__date__ = '2026-10-14'
# -----------------------------------------------------------------------------
# The URL to google (must have the "sheet_id" and "gid" parts)
GOOGLE_URL = 'https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}'
# Do not edit the following lines, these are the individual google sheet ids
SHEET_ID = '1hGPX_s_fUbEmjDtBbrWrlgwDFMC_Ek-63s1JCHnaIvA'
# sheet with list of papers
GID0 = '0'
# sheet with all affiliations
GID1 = '1318892288'
# sheet with the NIRPS authors (this could just be "authors")
GID2 = '831615847'
# sheet with the authors that are not NIRPS authors
#    (if you don't want a second sheet, just set this to None
GID3 = '223170284'
# sheet for the acknowledgements
GID4 = '671986807'
# allowed paper styles
ALLOWED_PAPER_STYLES = ['AJ', 'AANDA', 'SPIE']
# roles (ROLE column of the author sheets) of people who are not expected on
#    every paper; the team members with any other role who are not in a
#    paper's author list are listed at the end of the report
ROLES_NOT_REQUIRED = ['OTHER', 'COLL', 'EXCLUDE', 'INTERN', 'BUILDER']
# The A&A author block follows the aa.cls v9.4 format: \corrauth{} for the
#    corresponding author and one \email{} per co-author (read by the A&A
#    editorial system, not printed). Older versions of the class have no
#    \corrauth and print every \email{} in the author list, so these lines are
#    written in front of the author block to give them the v9.4 behaviour
#    (they do nothing with v9.4 itself)
AANDA_COMPAT = r"""% Only acts with A&A classes older than v9.4 (does nothing otherwise): defines
% \corrauth and keeps the co-author e-mails out of the printed author list.
\makeatletter
\@ifundefined{corrauth}{%
\newcommand*{\corrauth}[1]{\thanks{Corresponding author: {\ttfamily #1}}}%
\@ifundefined{aa@authorfont}{}{\g@addto@macro\aa@authorfont{\renewcommand*{\email}[1]{\unskip}}}%
}{}
\makeatother
"""

# -----------------------------------------------------------------------------
# Define a translation between accented letters to the latex equivalent
LETTER_2_LATEX = dict()
LETTER_2_LATEX['_'] = "\\_"
LETTER_2_LATEX['é'] = "\\'e"
LETTER_2_LATEX['è'] = "\\`e"
LETTER_2_LATEX['ê'] = "\\^e"
LETTER_2_LATEX['à'] = "\\`a"
LETTER_2_LATEX['â'] = "\\^a"
LETTER_2_LATEX['ç'] = "\\c{c}"
LETTER_2_LATEX['ù'] = "\\`u"
LETTER_2_LATEX['û'] = "\\^u"
LETTER_2_LATEX['ô'] = "\\^o"
LETTER_2_LATEX['î'] = "\\^i"
LETTER_2_LATEX['ï'] = '\\"i'
LETTER_2_LATEX['ë'] = '\\"e'
LETTER_2_LATEX['ü'] = '\\"u'
LETTER_2_LATEX['ö'] = '\\"o'
LETTER_2_LATEX['ä'] = '\\"a'
LETTER_2_LATEX['ÿ'] = '\\"y'
LETTER_2_LATEX['É'] = "\\\'E"
LETTER_2_LATEX['È'] = "\\`E"
LETTER_2_LATEX['Ê'] = "\\^E"
LETTER_2_LATEX['À'] = "\\`A"
LETTER_2_LATEX['Â'] = "\\^A"
LETTER_2_LATEX['Ç'] = "\\c{C}"
LETTER_2_LATEX['Ù'] = "\\`U"
LETTER_2_LATEX['Û'] = "\\^U"
LETTER_2_LATEX['Ô'] = "\\^O"
LETTER_2_LATEX['Î'] = "\\^I"
LETTER_2_LATEX['Ï'] = '\\"I'
LETTER_2_LATEX['Ë'] = '\\"E'
LETTER_2_LATEX['Ü'] = '\\"U'
LETTER_2_LATEX['Ö'] = '\\"O'
LETTER_2_LATEX['Ä'] = '\\"A'
LETTER_2_LATEX['Ÿ'] = '\\"Y'
LETTER_2_LATEX['á'] = "\\'a"
LETTER_2_LATEX['í'] = "\\'i"
LETTER_2_LATEX['ó'] = "\\'o"
LETTER_2_LATEX['ú'] = "\\'u"
LETTER_2_LATEX['ñ'] = '\\~n'
LETTER_2_LATEX['Á'] = "\\'A"
LETTER_2_LATEX['Í'] = "\\'I"
LETTER_2_LATEX['Ó'] = "\\'O"
LETTER_2_LATEX['Ú'] = "\\'U"
LETTER_2_LATEX['Ñ'] = '\\~N'
LETTER_2_LATEX['ã'] = '\\~a'
LETTER_2_LATEX['õ'] = '\\~o'
LETTER_2_LATEX['Ã'] = '\\~A'
LETTER_2_LATEX['Õ'] = '\\~O'


# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # print 'Hello World!'
    print("Hello World!")

# =============================================================================
# End of code
# =============================================================================
