import bibtexparser
from langdetect import detect

def remove_useless_papers(bibtex_file, output_file):
    with open(bibtex_file) as bibtex_file:
        bibtex_str = bibtex_file.read()

    bib_database = bibtexparser.loads(bibtex_str)

    total_entries = len(bib_database.entries)

    removed_entries = []
    new_entries = []

    for entry in bib_database.entries:
        language = entry.get("language")
        if language is None or language.strip() == "":
            try: 
                entry["language"] = 'english' if detect(entry.get('abstract', '')) == 'en' else 'other'
            except:
                entry["language"] = 'unknown'
        if (
            ("booktitle" in entry and "workshop" in entry["booktitle"].lower()) or
            ("title" in entry and "proceedings" in entry["title"].lower()) or
            (entry["language"].lower() != "english") or 
            ("abstract" not in entry) or
            (entry["abstract"].strip() == "") or
            ("art performance" in entry["abstract"].lower())
        ):
            removed_entries.append(entry)
        else:
            new_entries.append(entry)

    bib_database.entries = new_entries

    with open(output_file, "w") as bibtex_file:
        bibtexparser.dump(bib_database, bibtex_file)

    if removed_entries:
        print("\nRemoved entries:")
        for entry in removed_entries:
            print(entry.get("title"))

    print(f"Total number of entries: {total_entries}")
    print(f"Number of entries removed: {len(removed_entries)}")
    print(f"Number of entries remaining after removal: {len(new_entries)}")


# Use the function
remove_useless_papers(
    "/home/evilscript/Downloads/NPC & AI.bib", "/home/evilscript/Downloads/output.bib"
)