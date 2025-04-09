"""Example script to generate random subsets for manual labeling."""

from pepbench.datasets import EmpkinsDataset

from pepbench_annotation.helpers import generate_labeling_borders
from pepbench_annotation.utils import get_dataset_path

if __name__ == "__main__":
    dataset_path = get_dataset_path("empkins")
    dataset = EmpkinsDataset(dataset_path)

    dict_labeling_borders = generate_labeling_borders(
        dataset, phase_durations={"Prep": 60, "Pause_1": 30, "Talk": 60, "Math": 60, "Pause_5": 30}, random_seed=0
    )

    for key, df in dict_labeling_borders.items():
        folder_path = dataset_path.joinpath(f"{'/'.join(key)}")
        folder_path.mkdir(parents=True, exist_ok=True)
        file_path = folder_path.joinpath(f"{'_'.join(key)}_labeling_borders.csv")
        df.to_csv(file_path, index=False)
