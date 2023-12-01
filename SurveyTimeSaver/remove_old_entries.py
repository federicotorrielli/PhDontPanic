import bibtexparser


def remove_old_entries(bibtex_file, output_file):
    with open(bibtex_file) as bibtex_file:
        bibtex_str = bibtex_file.read()

    bib_database = bibtexparser.loads(bibtex_str)

    total_entries = len(bib_database.entries)
    old_entries = [
        entry
        for entry in bib_database.entries
        if "year" in entry and is_old(entry["year"])
    ]

    new_entries = [
        entry
        for entry in bib_database.entries
        if "year" not in entry or not is_old(entry["year"])
    ]

    bib_database.entries = new_entries

    with open(output_file, "w") as bibtex_file:
        bibtexparser.dump(bib_database, bibtex_file)

    print(f"Total number of entries: {total_entries}")
    print(f"Number of entries removed: {len(old_entries)}")
    print(f"Number of entries remaining after removal: {len(new_entries)}")


def is_old(year_str):
    try:
        year = int(year_str)
        return year <= 2013
    except ValueError:
        # If the year can't be converted to an integer, try extracting the year from the string
        year_parts = [int(part) for part in year_str.split() if part.isdigit()]
        if year_parts:
            return min(year_parts) <= 2013

    # If no year can be determined, assume the entry is not old
    return False


# Use the function
remove_old_entries(
    "/home/evilscript/Downloads/input.bib", "/home/evilscript/Downloads/output.bib"
)
