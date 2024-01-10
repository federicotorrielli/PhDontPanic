import os
import time
import urllib.parse

import bibtexparser
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

# Path to the directory where you'll download the PDFs.
DOWNLOAD_DIR = "/home/evilscript/Downloads/"

# Path to your .bib file.
BIB_FILE_PATH = "/home/evilscript/Downloads/refs.bib"

# Load the .bib file and parse the entries.
with open(BIB_FILE_PATH) as bibtex_file:
    bib_database = bibtexparser.load(bibtex_file)

existing_filenames = set(os.listdir(DOWNLOAD_DIR))


class NewFileHandler(FileSystemEventHandler):
    def on_created(self, event):
        # Only proceed if the new file is a PDF
        if event.is_directory or not event.src_path.endswith(".pdf"):
            return
        print(f"New file detected: {event.src_path}")
        # Stop the observer if needed.
        observer.stop()


# Function to format the new filename.
def format_filename(entry):
    # Extract the year, first author's last name, and a slugified title.
    year = entry.get("year", "????")
    author = entry["author"].split(" and ")[0].split(",")[0]
    title_words = entry["title"].replace("{", "").replace("}", "").split()
    title_slug = "-".join(title_words[:5])  # Use the first 5 words of the title.
    filename = f"{year}-{author}-{title_slug}.pdf"
    return filename


# Function to find the newest file in the directory.
def find_newest_pdf(download_dir, existing_files):
    current_files = set(os.listdir(download_dir))
    new_files = current_files - existing_files
    new_pdfs = [f for f in new_files if f.endswith(".pdf")]
    if not new_pdfs:
        return None
    newest_pdf = max(
        new_pdfs, key=lambda f: os.path.getctime(os.path.join(download_dir, f))
    )
    return newest_pdf


# Set up the observer to watch for new PDFs in the download directory.
observer = Observer()
event_handler = NewFileHandler()
observer.schedule(event_handler, DOWNLOAD_DIR, recursive=False)
observer.start()

# Loop through each entry in the .bib file.
no_doi = []
for entry in bib_database.entries:
    doi = entry.get("doi", "")
    title = entry.get("title", "No title available")
    author = entry["author"].split(" and ")[0]
    if doi:
        formatted_name = format_filename(entry)
        if formatted_name in existing_filenames:
            print(f"Duplicate detected, skipping: {formatted_name}")
            continue
        # Record the current state of the download directory.
        existing_files = set(os.listdir(DOWNLOAD_DIR))

        # Output the DOI link and the title + author.
        doi_link = f"https://doi.org/{urllib.parse.quote(doi)}"
        print(f"Please download the PDF from: {doi_link}")
        print(f"Title: {entry.get('title')}")
        print(f"Author: {entry.get('author')}")

        # Ask the user if they want to skip this file.
        skip = input("Press enter to skip, or any other key to download: ")
        if skip == "":
            continue

        # Wait for the PDF to be downloaded.
        print("Waiting for file to be downloaded...")
        observer.join()  # Wait until a file is created.

        # Add a small delay to give the observer time to detect the new file.
        time.sleep(2)

        # Find the newly downloaded PDF.
        newest_pdf = find_newest_pdf(DOWNLOAD_DIR, existing_files)
        if newest_pdf:
            # Format the new filename and rename the PDF.
            new_filename = format_filename(entry)
            newest_file_path = os.path.join(DOWNLOAD_DIR, newest_pdf)
            new_file_path = os.path.join(DOWNLOAD_DIR, new_filename)
            os.rename(newest_file_path, new_file_path)
            print(f"Renamed downloaded file to: {new_filename}")
            existing_filenames.add(formatted_name)
        else:
            print("No new PDF file detected. Please try downloading again.")

        # Restart the observer for the next file.
        observer.stop()
        observer = Observer()
        observer.schedule(event_handler, DOWNLOAD_DIR, recursive=False)
        observer.start()
    else:
        no_doi.append(entry)
        print(f"No DOI found for entry: {entry.get('title')}")

print(
    f"All files processed! {len(no_doi)} entries have no DOI.\nEntries with no DOI: {[e.get('title') for e in no_doi]}"
)
