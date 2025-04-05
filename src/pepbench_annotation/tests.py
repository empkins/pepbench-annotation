import json
from pathlib import Path

from pepbench.datasets import EmpkinsDataset

from pepbench_annotation.utils import generate_labeling_borders


def _get_dataset_path(dataset_type: str) -> Path:
    config_path = Path("../../config/config.json")
    config_dict = json.load(config_path.open("r"))
    return Path(config_dict[dataset_type])


if __name__ == "__main__":
    dataset_path = _get_dataset_path("empkins")
    dataset = EmpkinsDataset(dataset_path)

    generate_labeling_borders(
        dataset, phase_durations={"Prep": 60, "Pause_1": 30, "Talk": 60, "Math": 60, "Pause_5": 30}
    )
