import sys
import requests
import bibtexparser
import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

# Function to extract DOI
def extract_doi(doi):
    if doi.startswith("https://doi.org/"):
        return doi[len("https://doi.org/"):]
    return doi

# Function to get references for DOI
def get_referenced_dois(doi):
    if "arXiv" in doi:
        response = requests.get(f"https://api.semanticscholar.org/v1/paper/{doi}")
        return [ref['doi'] for ref in response.json()['references'] if ref['doi'] is not None]
    else:
        response = requests.get(f"https://opencitations.net/index/coci/api/v1/references/{doi}")
        return [ref['cited'] for ref in response.json()]

# Function to get bibtex entries
def get_bibtex_entries(doi_batch):
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(requests.get, f"https://doi.org/{doi}", headers={"Accept": "application/x-bibtex"}) for doi in doi_batch]
        return [future.result().text for future in tqdm.tqdm(as_completed(futures), total=len(doi_batch))]

# Function to save bibtex entries to file
def save_bibtex_to_file(bibtex_entries, filename="references.bib"):
    bib_database = bibtexparser.loads("".join(bibtex_entries))
    with open(filename, "w") as f:
        f.write(bibtexparser.dumps(bib_database))

def main():
    # Get the DOI from the command line arguments
    doi = extract_doi(sys.argv[1])
    referenced_dois = get_referenced_dois(doi)
    print(f"Found {len(referenced_dois)} references")

    # Split the DOIs into batches of 10
    doi_batches = [referenced_dois[i:i+10] for i in range(0, len(referenced_dois), 10)]

    # Use ThreadPoolExecutor to parallelize the requests to the Crossref API
    bibtex_entries = [entry for batch in doi_batches for entry in get_bibtex_entries(batch)]
    print(f"Found {len(bibtex_entries)} BibTeX entries")

    # Save the BibTeX entries to a file
    save_bibtex_to_file(bibtex_entries)
    print("Done")

if __name__ == "__main__":
    main()
