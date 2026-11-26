from pathlib import Path
import subprocess
import sys
import zipfile


PROJECT_ROOT = Path(__file__).resolve().parent
OUT = PROJECT_ROOT / "datasets" / "external"


HF_DATASETS = {
    "swe_qa": "swe-qa/SWE-QA-Benchmark",
    "ml_systems_interview_bench": "Max00035/ml-systems-interview-bench",
    "resume_skill_extractor": "keerthanshetty/resume-skill-extractor-dataset",
    "campus_recruitment": "Krooz/Campus_Recruitment_CSV",
}


HARMOGEN_URL = (
    "https://zenodo.org/records/19534458/files/"
    "harmogenr_dataset_v2.zip?download=1"
)


def download_huggingface(repo_id, folder_name):
    from huggingface_hub import snapshot_download

    destination = OUT / folder_name
    destination.mkdir(parents=True, exist_ok=True)

    print(f"\nDownloading: {repo_id}")
    print(f"Destination: {destination}")

    snapshot_download(
        repo_id=repo_id,
        repo_type="dataset",
        local_dir=str(destination),
    )

    print(f"Completed: {repo_id}")


def download_harmogen():
    import requests

    folder = OUT / "harmogen_r"
    folder.mkdir(parents=True, exist_ok=True)

    zip_file = folder / "harmogenr_dataset_v2.zip"

    if zip_file.exists():
        print("\nHARMOGEN-R already downloaded.")
        return zip_file

    print("\nDownloading HARMOGEN-R...")
    print("This may take some time.")

    response = requests.get(
        HARMOGEN_URL,
        stream=True,
        timeout=120
    )

    response.raise_for_status()

    total = int(response.headers.get("content-length", 0))
    downloaded = 0

    with open(zip_file, "wb") as file:

        for chunk in response.iter_content(
            chunk_size=1024 * 1024
        ):

            if not chunk:
                continue

            file.write(chunk)

            downloaded += len(chunk)

            if total:
                percentage = downloaded * 100 / total

                print(
                    f"\rProgress: {percentage:.1f}%",
                    end="",
                    flush=True
                )

    print("\nHARMOGEN-R download completed.")

    return zip_file


def extract_harmogen(zip_file):

    folder = OUT / "harmogen_r"
    extracted = folder / "extracted"

    marker = extracted / ".done"

    if marker.exists():
        print("HARMOGEN-R already extracted.")
        return

    extracted.mkdir(parents=True, exist_ok=True)

    print("\nExtracting HARMOGEN-R...")
    print("This may take some time.")

    with zipfile.ZipFile(zip_file, "r") as archive:

        archive.extractall(extracted)

    marker.write_text("done", encoding="utf-8")

    print("HARMOGEN-R extraction completed.")


def main():

    print("=" * 70)
    print("NEXORA DATASET DOWNLOADER")
    print("=" * 70)

    OUT.mkdir(parents=True, exist_ok=True)

    print(f"\nData will be stored in:")
    print(OUT)

    print("\nStarting downloads...\n")

    # Hugging Face datasets
    for folder_name, repo_id in HF_DATASETS.items():

        try:

            download_huggingface(
                repo_id,
                folder_name
            )

        except Exception as error:

            print(f"\nERROR downloading {repo_id}")
            print(error)

    # HARMOGEN-R
    try:

        zip_file = download_harmogen()

        extract_harmogen(zip_file)

    except Exception as error:

        print("\nERROR downloading HARMOGEN-R")
        print(error)

    print("\n" + "=" * 70)
    print("DATASET DOWNLOAD PROCESS FINISHED")
    print("=" * 70)

    print("\nCheck this folder:")
    print(OUT)


if __name__ == "__main__":
    main()