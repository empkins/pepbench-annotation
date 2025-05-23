import numpy as np
import pandas as pd
from biopsykit.signals.ecg.segmentation import HeartbeatSegmentationNeurokit
from pepbench.datasets import BasePepDataset


def generate_labeling_borders(
    dataset: BasePepDataset,
    phase_durations: dict[str, int],
    random_seed: int = 0,
) -> dict[tuple[str, ...], pd.DataFrame]:
    return_dict = {}
    group_levels = list(dataset.index.columns)
    for subset in dataset.groupby(group_levels[:-1]):
        label_borders = []
        for subset_phase in subset.groupby(group_levels[-1]):
            phase_name = subset_phase.group_labels[0][-1]
            # get the duration of the randomly selected subset
            duration_subset = phase_durations[phase_name]

            # segment the ECG data into heartbeats to determine the start and end of the labeling borders
            ecg_data = subset_phase.ecg
            heartbeat_segmentation_algo = HeartbeatSegmentationNeurokit()
            heartbeat_segmentation_algo.extract(ecg=ecg_data, sampling_rate_hz=subset_phase.sampling_rate_ecg)
            heartbeats = heartbeat_segmentation_algo.heartbeat_list_
            heartbeats = heartbeats.assign(
                heartbeat_length_ms=(heartbeats["end_sample"] - heartbeats["start_sample"])
                / subset_phase.sampling_rate_ecg
                * 1000
            )
            heartbeats = heartbeats.assign(
                end_time=heartbeats["start_time"] + pd.to_timedelta(heartbeats["heartbeat_length_ms"], unit="ms")
            )
            heartbeats_second = heartbeats["end_time"] - heartbeats["end_time"].iloc[0]
            # compute the maximum possible start value
            max_start_val = heartbeats_second.iloc[-1] - pd.Timedelta(seconds=duration_subset)
            min_idx = 0
            # get the closest heartbeat_id index to the max_start_val
            max_idx = heartbeats_second.sub(max_start_val).abs().idxmin()

            rng = np.random.default_rng(seed=random_seed)
            # randomly select a start index between min_idx and max_idx
            start_idx = min_idx + int((max_idx - min_idx) * rng.random())
            start_idx = heartbeats["start_sample"].iloc[start_idx]
            end_idx = start_idx + duration_subset * subset_phase.sampling_rate_ecg

            # get the subset
            subsubset_random = ecg_data.iloc[start_idx:end_idx]

            df_labeling_borders_start = pd.DataFrame(
                {
                    "timestamp": subsubset_random.index[0],
                    "description": f"{{'{phase_name}': 'start'}}",
                    "sample_absolute": start_idx,
                    "sample_relative": start_idx,
                },
                index=[0],
            )
            df_labeling_borders_end = pd.DataFrame(
                {
                    "timestamp": subsubset_random.index[-1],
                    "description": f"{{'{phase_name}': 'end'}}",
                    "sample_absolute": end_idx,
                    "sample_relative": end_idx,
                },
                index=[0],
            )
            label_borders.append(df_labeling_borders_start)
            label_borders.append(df_labeling_borders_end)

        label_borders_df = pd.concat(label_borders, ignore_index=True)
        return_dict[tuple(subset.group_labels[0])] = label_borders_df

    return return_dict
