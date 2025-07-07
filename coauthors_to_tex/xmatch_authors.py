import numpy as np
from rapidfuzz import process, fuzz
from astropy.table import Table
from coauthors_to_tex import constants
from coauthors_to_tex import general
import argparse

SCORE_MIN = 80  # Default minimum score for matching

def main():

    parser = argparse.ArgumentParser(description="Match co-authors from a list")
    parser.add_argument(
        '--score_min',
        type=float,
        default=SCORE_MIN,
        help='Minimum score for matching authors (default: 80)',
    )
    parser.add_argument(
        '--sort',
        action='store_true',
        default=False,
        help='Sort the output by author name (default: False)',
    )
    args = parser.parse_args()
    score_min = args.score_min
    sorted = args.sort

    sheet_id = constants.SHEET_ID
    gid0, gid1 = constants.GID0, constants.GID1
    gid2, gid3 = constants.GID2, constants.GID3
    gid4 = constants.GID4

    tbl_authors, _ = general.get_tbl_authors(sheet_id,gid2, gid3, gid4)

    if sorted:
        tbl_authors = tbl_authors[np.argsort(tbl_authors['Last Name'])]
    tbl_authors['ID'] = np.arange(len(tbl_authors))

    # Allow multiline input: keep reading lines until an empty line is entered
    lines = []
    print("Enter the co-authors to match, comma separated and can be on multiple lines (empty line to finish):")
    while True:
        line = input()
        if line.strip() == "":
            break
        lines.append(line)
    if lines:
        input_coauthors = ' '.join(lines)

    input_coauthors = [name.strip() for name in input_coauthors.split(',')]
    # remove any that is less than 2 characters
    input_coauthors = [name for name in input_coauthors if len(name) > 1]

    # Precompute normalized AUTHOR list
    normalized_authors = [general.normalize_name(author) for author in tbl_authors['AUTHOR']]

    # Match each external name
    matches = []
    for name in input_coauthors:
        norm_name = general.normalize_name(name)
        best_match, score, idx = process.extractOne(
            norm_name, normalized_authors, scorer=fuzz.token_sort_ratio
        )
        matched_shortname = tbl_authors['SHORTNAME'][idx] if score > score_min else 'NO MATCH'
        matches.append((name, tbl_authors['AUTHOR'][idx], matched_shortname, score,idx))

    tbl_out = Table()
    tbl_out['INPUT_NAMES'] = [matches[i][0] for i in range(len(matches))]
    tbl_out['MATCHED_AUTHOR'] = [matches[i][1] for i in range(len(matches))]
    tbl_out['SHORTNAME'] = [matches[i][2] for i in range(len(matches))]
    tbl_out['SCORE'] = [matches[i][3] for i in range(len(matches))]
    tbl_out['ID'] = [matches[i][4] for i in range(len(matches))]

    if sorted:
        tbl_out = tbl_out[np.argsort(tbl_out['ID'])]

    # Display results
    for ext_name, matched_author, shortname, score,_ in matches:
        # change color from green to red if score is below score_min
        if score < score_min:   
            color = '\033[91m'  # Red
            reset_color = '\033[0m'  # Reset color
        else:
            color = '\033[92m'  # Green
            reset_color = '\033[0m'  # Reset color
        # Print the result with color
        if shortname == 'NO MATCH':
            print(f"{color}{ext_name:30} --> {'? ' + matched_author + ' ?':35} | {shortname:16} (score: {score:.2f}%) {reset_color}")
        else:
            print(f"{color}{ext_name:30} --> {matched_author:35} | {shortname:16} (score: {score:.2f}%) {reset_color}")

    if np.min(tbl_out['SCORE']) > score_min:
        print('\n' + '~' * general.get_terminal_width())
        merged_short = ','.join(tbl_out['SHORTNAME'])

        print(f"Merged short names: {merged_short}")

    else:
        print('\n' + '~' * general.get_terminal_width())
        print(f"Some authors were not matched with a score above {score_min}%.")
        print("Please check the output and adjust the input if necessary.")
        print('\n' + '~' * general.get_terminal_width())
