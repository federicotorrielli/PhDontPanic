import pickle
import time
from tqdm import tqdm
import bibtexparser
from poe_api_wrapper import PoeApi

def create_prompts(file: str) -> dict:
    with open(file) as bibtex_file:
        bib_database = bibtexparser.load(bibtex_file)

    prompts = {
        f"Given the following paper, respond 'yes' if the paper is strictly about AI and its use in Video games/Serious games, 'no' otherwise. Don't write anything else.\n"
        f"Paper: {entry['title']}\n"
        f"{'Abstract: ' + entry['abstract'] + '\n' if 'abstract' in entry else ''}"
        f"{'Keywords: ' + entry['keywords'] + '\n' if 'keywords' in entry else ''}"
        f"Response: ": entry
        for entry in bib_database.entries
    }

    return prompts


def save_bibtex(outputs: list, prompts: dict, output_file_name: str) -> None:
    """
    Append the bibtex entry if the output is yes to the output file
    """
    good_bibtex = []

    for output in outputs:
        prompt = output.prompt
        bibtex = prompts[prompt]
        generated_text = output.text.lower()
        if not isinstance(generated_text, str):
            continue
        if "yes" in generated_text:
            good_bibtex.append(bibtex)

    db = bibtexparser.bibdatabase.BibDatabase()
    db.entries = good_bibtex
    writer = bibtexparser.bwriter.BibTexWriter()
    with open(output_file_name, "w") as f:
        f.write(writer.write(db))


if __name__ == "__main__":
    prompts = create_prompts("file.bib")
    client = PoeApi("wkb2sdkdpf8BH1TJsW4sQg%3D%3D")  # Add your token here
    bot = "Assistant"  # Add the bot name you want to use here
    outputs = []
    chat_code = None

    MAX_RETRIES = 5
    RETRY_DELAY = 10  # delay in seconds
    MESSAGE_DELAY = 5  # delay between each message

    for prompt in tqdm(prompts.keys(), desc="Processing prompts"):
        for attempt in range(MAX_RETRIES):
            try:
                if chat_code is None:
                    chunk = next(client.send_message(bot, prompt))
                    chat_code = chunk["chatCode"]
                else:
                    chunk = next(client.send_message(bot, prompt, chatCode=chat_code))
                outputs.append(chunk)
                break  # if the message was sent successfully, break the retry loop
            except RuntimeError as e:
                print(f"Error on attempt {attempt + 1}: {e}")
                if attempt < MAX_RETRIES - 1:  # no need to sleep on the last attempt
                    time.sleep(RETRY_DELAY)
        time.sleep(MESSAGE_DELAY)

    # Save outputs to local file using pickle
    with open("outputs.pkl", "wb") as f:
        pickle.dump(outputs, f)

    save_bibtex(outputs, prompts, "output.bib")