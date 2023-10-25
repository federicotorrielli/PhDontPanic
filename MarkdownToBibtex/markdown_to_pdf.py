import re
import subprocess
import sys


def remove_emojis(file_path):
    """Removes any emoji from a markdown file"""
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()

    # Remove emojis
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags (iOS)
        "\U00002500-\U00002BEF"  # chinese characters
        "\U00002702-\U000027B0"
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "\U0001f926-\U0001f937"
        "\U00010000-\U0010ffff"
        "\u2640-\u2642"
        "\u2600-\u2B55"
        "\u200d"
        "\u23cf"
        "\u23e9"
        "\u231a"
        "\ufe0f"  # dingbats
        "\u3030"
        "]+",
        flags=re.UNICODE,
    )

    no_emoji_content = emoji_pattern.sub(r"", content)

    # Write the altered content back to the file
    with open(file_path, "w", encoding="utf8") as file:
        file.write(no_emoji_content)


def convert_md_to_latex(file_path):
    """Converts the cleaned markdown file to LaTeX using Pandoc"""
    output_file = file_path.replace(".md", ".tex")
    header_file = "header.tex"

    # Write enumitem configuration to header file
    with open(header_file, "w") as file:
        file.write(
            r"\usepackage{enumitem}"
            "\n"
            r"\setlistdepth{9}"
            "\n"
            r"\setlist[itemize,1]{label=$\bullet$}"
            "\n"
            r"\setlist[itemize,2]{label=$\bullet$}"
            "\n"
            r"\setlist[itemize,3]{label=$\bullet$}"
            "\n"
            r"\setlist[itemize,4]{label=$\bullet$}"
            "\n"
            r"\setlist[itemize,5]{label=$\bullet$}"
            "\n"
            r"\setlist[itemize,6]{label=$\bullet$}"
            "\n"
            r"\setlist[itemize,7]{label=$\bullet$}"
            "\n"
            r"\setlist[itemize,8]{label=$\bullet$}"
            "\n"
            r"\setlist[itemize,9]{label=$\bullet$}"
            "\n"
            r"\renewlist{itemize}{itemize}{9}"
        )

    subprocess.call(
        [
            "pandoc",
            "-s",
            "--include-in-header=" + header_file,
            file_path,
            "-o",
            output_file,
        ]
    )
    return output_file


def compile_latex_to_pdf(file_path):
    """Compiles the LaTeX file to PDF using the Tectonic engine"""
    subprocess.call(["tectonic", file_path])


def main(file_path):
    remove_emojis(file_path)
    latex_file = convert_md_to_latex(file_path)
    compile_latex_to_pdf(latex_file)


if __name__ == "__main__":
    main(sys.argv[1])
