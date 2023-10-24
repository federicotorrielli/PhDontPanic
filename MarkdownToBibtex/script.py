import re
import arxiv
import bibtexparser
from bibtexparser.bwriter import BibTexWriter


def extract_arxiv_ids(markdown_content):
    pattern = r"https?://arxiv.org/abs/([0-9]+\.[0-9v]+)"
    matches = re.findall(pattern, markdown_content)
    return matches


def fetch_arxiv_paper(arxiv_id):
    search = arxiv.Search(id_list=[arxiv_id])
    paper = next(arxiv.Client().results(search))
    return paper


def generate_bibtex_entry(paper):
    entry = {
        "ENTRYTYPE": "article",
        "ID": str(paper.get_short_id()),
        "title": str(paper.title),
        "author": " and ".join([str(author.name) for author in paper.authors]),
        "year": str(paper.published.year),
        "url": str(paper.entry_id),
        "abstract": str(paper.summary),
        "arxivId": str(paper.get_short_id()),
    }
    if paper.journal_ref:
        entry["journal"] = str(paper.journal_ref)
    if paper.doi:
        entry["doi"] = str(paper.doi)
    return entry


def write_bibtex_file(entries, filename):
    db = bibtexparser.bibdatabase.BibDatabase()
    db.entries = entries
    writer = BibTexWriter()

    with open(filename, "w") as bibtex_file:
        bibtex_file.write(writer.write(db))


def main():
    import sys

    markdown_filename = "your_markdown_file.md"
    bibtex_filename = "output.bib"

    # If there's no md file, take the first argument as the md file name
    # If there are two arguments, take the second as the output file name
    if len(sys.argv) > 1:
        markdown_filename = sys.argv[1]
    if len(sys.argv) > 2:
        bibtex_filename = sys.argv[2]

    with open(markdown_filename, "r") as markdown_file:
        markdown_content = markdown_file.read()

    arxiv_ids = extract_arxiv_ids(markdown_content)
    bibtex_entries = []

    for arxiv_id in arxiv_ids:
        paper = fetch_arxiv_paper(arxiv_id)
        bibtex_entry = generate_bibtex_entry(paper)
        bibtex_entries.append(bibtex_entry)

    write_bibtex_file(bibtex_entries, bibtex_filename)


if __name__ == "__main__":
    main()
