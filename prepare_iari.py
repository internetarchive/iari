import os
import config

def create_json_folders():
    base_path = config.subdirectory_for_json
    subfolders = [
        "articles",
        "articlesV2",
        "dois",
        "pdfs",
        "probes",
        "references",
        "urls",
        "xhtmls"
    ]

    for folder in subfolders:
        full_path = os.path.join(base_path, folder)
        os.makedirs(full_path, exist_ok=True)
        print(f"Created: {full_path}")


if __name__ == "__main__":
    create_json_folders()