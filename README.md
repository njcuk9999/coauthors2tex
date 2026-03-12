# coauthors2tex

**Automatically generate publication-ready LaTeX author lists from a shared Google Spreadsheet.**

No more copy-pasting author names, affiliations, or acknowledgements by hand. Just maintain a shared Google Sheet and let `coauthors2tex` generate the correct LaTeX block for your journal — in seconds.

Supports **Astronomy & Astrophysics (A&A)** and **Astronomical Journal (AJ)** formats.

---

## Table of Contents

- [What does it do?](#what-does-it-do)
- [Installation](#installation)
- [How to run](#how-to-run)
- [Tools](#tools)
- [Google Sheet structure](#google-sheet-structure)
- [How to update the NIRPS author list](#how-to-update-the-nirps-author-list)
- [Forking for your own consortium](#forking-for-your-own-consortium)
- [Troubleshooting](#troubleshooting)

---

## What does it do?

`coauthors2tex` reads a shared Google Spreadsheet containing:

- A list of papers (author order, journal style, acknowledgements)
- A database of author names, emails, ORCIDs, and affiliations
- A list of acknowledgement text blocks

It then generates a `.tex` snippet ready to paste into your LaTeX paper, including:

- The `\author{}` / `\institute{}` block (or `\affiliation{}` for AJ)
- The acknowledgements paragraph

### Supported journal formats

| Style key | Journal | Author block format |
|-----------|---------|---------------------|
| `AANDA`   | Astronomy & Astrophysics | `\author{...\and ...}` + `\institute{...}` |
| `AJ`      | Astronomical Journal | `\author[orcid]{...}` + `\affiliation{...}` per author |

> **A&A note:** ORCIDs are **not** inserted in the A&A LaTeX block. Per A&A policy, only ORCIDs authenticated through the journal's submission system will be published — any ORCID added manually to the manuscript will be removed.

---

## Installation

### Step 1: Clone the repository

```bash
git clone https://github.com/njcuk9999/coauthors2tex.git
```

> If you get a permission error with `git@github.com:...`, use the `https://` URL above.

### Step 2: Create a Python environment

Using **conda** (recommended):

```bash
conda create --name coauthors-env python=3.11
conda activate coauthors-env
```

Using **venv** (alternative):

```bash
python -m venv coauthors-env
source coauthors-env/bin/activate   # macOS / Linux
```

### Step 3: Install the package

```bash
cd coauthors2tex
pip install -U -e .
```

That's it! The `coauthors2tex` and `coauthorsxmatch` commands are now available in your environment.

---

## How to run

First, activate your environment:

```bash
conda activate coauthors-env
```

Then run:

```bash
coauthors2tex
```

The tool will:

1. Fetch the paper list, affiliations, and author database from Google Sheets (takes a few seconds)
2. Display a numbered list of available papers
3. Ask you to pick one
4. Print the LaTeX code to the terminal **and** save it to `{paper_key}_coauthors.tex`

Paste the `\author{}` / `\institute{}` block near the top of your `.tex` file, and the acknowledgements block inside `\begin{acknowledgements}...\end{acknowledgements}`.

---

## Tools

### `coauthors2tex` — generate an author list

The main tool. Generates the full LaTeX author list for a paper defined in the spreadsheet.

```bash
coauthors2tex
```

**Example A&A output:**

```latex
\author{
\'E. Artigau\inst{1,2}\corrauth{etienne.artigau@umontreal.ca}
\and N. Cook\inst{3}\email{neil.cook@univ.ca}
\and J. Bouchy\inst{4}
}

\institute{
\inst{1}Université de Montréal, Montréal, Canada\\
\inst{2}Observatoire du Mont-Mégantic, Montréal, Canada\\
\inst{3}University of Geneva, Geneva, Switzerland\\
\inst{4}Observatoire de Haute-Provence, France\\
}
```

---

### `coauthorsxmatch` — match external co-authors to the database

Useful when a collaborator sends you a draft with a co-author list that uses different name formats. This tool fuzzy-matches their names to the entries in the NIRPS database and returns the correct SHORTNAMEs to use in the spreadsheet.

```bash
coauthorsxmatch
```

Paste a comma-separated list of names (multi-line input is supported; press **Enter** on an empty line to finish). The tool prints each match with a confidence score and, if all scores are above the threshold, outputs the merged SHORTNAME list ready to paste into the `papers` sheet.

**Options:**

```
--score_min FLOAT   Minimum match score, 0–100 (default: 80)
--sort              Sort output alphabetically by matched last name
```

---

## Google Sheet structure

The tool reads from the [NIRPS author list spreadsheet](https://docs.google.com/spreadsheets/d/1hGPX_s_fUbEmjDtBbrWrlgwDFMC_Ek-63s1JCHnaIvA/edit?usp=sharing), which has 5 sheets:

| Sheet | Content |
|-------|---------|
| `papers` | One row per paper: key, style, ordered author list, acknowledgements |
| `affiliations` | Unique affiliations, each with a short key |
| `nirps_authors` | NIRPS team members |
| `other_authors` | External co-authors (same columns as `nirps_authors`) |
| `acknowledgements` | Acknowledgement text blocks, each with a key |

### `papers` sheet columns

| Column | Description |
|--------|-------------|
| `paper key` | Short identifier used as the output filename, e.g. `cook2024` |
| `STYLE` | Journal format: `AJ` or `AANDA` |
| `author list` | Comma-separated SHORTNAMEs **in author order** |
| `ACKNOWLEDGEMENTS` | Comma-separated acknowledgement keys (`0` if none) |
| `Program ID` | Observing program ID (optional, for reference) |
| `Overleaf Link` | Link to the Overleaf project (optional, for reference) |

### `nirps_authors` / `other_authors` sheet columns

| Column | Description |
|--------|-------------|
| `AUTHOR` | Full name as it will appear in LaTeX, e.g. `\'E. Artigau` |
| `Last Name` | Used to generate initials for acknowledgements |
| `First Name` | Used to generate initials for acknowledgements |
| `ORCID` | 16-character ORCID (format: `0000-0000-0000-0000`); used for AJ only |
| `EMAIL` | Author email address |
| `SHORTNAME` | Unique key used to reference this author in the `papers` sheet |
| `AFFILIATIONS` | Comma-separated affiliation SHORTNAMEs (must exist in the `affiliations` sheet) |
| `ACKNOWLEDGEMENTS` | Comma-separated acknowledgement keys (`0` if none) |

### `affiliations` sheet columns

| Column | Description |
|--------|-------------|
| `SHORTNAME` | Short key referenced in author `AFFILIATIONS` columns |
| `AFFILIATION` | Full affiliation string. **Must end with `, Country`** (e.g. `Université de Montréal, Canada`) |

---

## How to update the NIRPS author list

1. Open the [NIRPS Google Spreadsheet](https://docs.google.com/spreadsheets/d/1hGPX_s_fUbEmjDtBbrWrlgwDFMC_Ek-63s1JCHnaIvA/edit?usp=sharing)
2. **New paper** → add a row in the `papers` sheet with the author SHORTNAMEs in order
3. **New affiliation** → add a row in the `affiliations` sheet
4. **New NIRPS team member** → add a row in the `nirps_authors` sheet
5. **New external co-author** → add a row in the `other_authors` sheet

---

## Forking for your own consortium

To adapt this tool for a different author database, create your own Google Spreadsheet with the same column structure as described above, make it accessible (share with "Anyone with the link can view"), then edit `coauthors_to_tex/constants.py`:

```python
SHEET_ID = 'your-google-sheet-id'   # The long ID in the spreadsheet URL
GID0 = '0'                          # Tab ID for papers
GID1 = '...'                        # Tab ID for affiliations
GID2 = '...'                        # Tab ID for primary authors
GID3 = '...'                        # Tab ID for secondary authors (or None)
GID4 = '...'                        # Tab ID for acknowledgements
```

To find a tab's GID: click on the tab in your browser — the URL will end with `#gid=XXXXXXXX`.

---

## Troubleshooting

**`the author X is not in the list of authors`**
The SHORTNAME in the `papers` sheet doesn't match any entry in the author sheets. Check for typos or extra spaces.

**`the affiliation X is not in the list of affiliations`**
An author's `AFFILIATIONS` value contains a SHORTNAME that doesn't exist in the `affiliations` sheet. Check for typos.

**`the country X is not valid`**
Affiliations must end with `, Country` where the country name is recognized (e.g. `Canada`, `France`, `United States`). Check the last part of the affiliation string.

**`too many iterations to find unique initials`**
Two authors share initials that cannot be resolved by adding more letters. Contact the maintainer or manually disambiguate.

**Scores too low in `coauthorsxmatch`**
Try lowering the threshold: `coauthorsxmatch --score_min 60`. Names with non-ASCII characters or unusual formatting may score lower.

---

*Maintained by Étienne Artigau & Neil Cook*

