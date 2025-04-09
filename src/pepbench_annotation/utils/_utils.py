import json
from pathlib import Path


def get_dataset_path(dataset_type: str) -> Path:
    config_path = Path("../../config/config.json")
    config_dict = json.load(config_path.open("r"))
    return Path(config_dict[dataset_type])
