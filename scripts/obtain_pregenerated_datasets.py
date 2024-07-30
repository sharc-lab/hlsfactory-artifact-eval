import shutil
from pathlib import Path

import urllib3
from utils.utils import get_env_vars

DATASET_FILE_NAMES = [
    "hlsfactory_workdir_design_space_base.tar.gz",
    "hlsfactory_workdir_design_space_sampled.tar.gz",
    "hlsfactory_workdir_parallel_test_run.tar.gz",
    "hlsfactory_workdir_regression_testing.tar.gz",
    "hlsfactory_intel_data.tar.gz",
]

DIR_DATASETS = get_env_vars(["DIR_DATASETS"])["DIR_DATASETS"]
assert isinstance(DIR_DATASETS, Path)

if DIR_DATASETS.exists():
    shutil.rmtree(DIR_DATASETS)
DIR_DATASETS.mkdir(parents=True, exist_ok=True)


def download_data_zenodo():
    BASE_URL = "https://zenodo.org/records/13131703/files/"

    for dataset_file_name in DATASET_FILE_NAMES:
        download_url = BASE_URL + dataset_file_name
        download_path = DIR_DATASETS / dataset_file_name

        print(f"Downloading {dataset_file_name} from {download_url}")

        with urllib3.PoolManager() as http:
            with http.request(
                "GET", download_url, preload_content=False
            ) as r, download_path.open("wb") as out_file:
                shutil.copyfileobj(r, out_file)

        shutil.unpack_archive(download_path, extract_dir=DIR_DATASETS)


def download_data_hlsyn():
    HLSYN_URL = "https://github.com/ZongyueQin/HLSyn/raw/main/data/HLSyn_data.tar.gz"
    HLSYN_FILE_NAME = "HLSyn_data.tar.gz"

    download_path = DIR_DATASETS / HLSYN_FILE_NAME

    print(f"Downloading {HLSYN_FILE_NAME} from {HLSYN_URL}")

    with urllib3.PoolManager() as http:
        with http.request(
            "GET", HLSYN_URL, preload_content=False
        ) as r, download_path.open("wb") as out_file:
            shutil.copyfileobj(r, out_file)

    shutil.unpack_archive(download_path, extract_dir=DIR_DATASETS / "HLSyn_data")


if __name__ == "__main__":
    download_data_zenodo()
    download_data_hlsyn()
