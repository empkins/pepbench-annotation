import json
from pathlib import Path


import pandas as pd


from pepbench.datasets import EmpkinsDataset

from pepbench.algorithms.heartbeat_segmentation import HeartbeatSegmentationNeurokit

from mad_gui.components.dialogs import UserInformation
from mad_gui.plugins.base import BaseDataImporter, SensorDataDict
from typing import Dict, List

from biopsykit.signals.icg.preprocessing import IcgPreprocessingBandpass
from biopsykit.signals.ecg.preprocessing import EcgPreprocessingNeurokit


class EmpkinsImporter(BaseDataImporter):
    def load_sensor_data(self, index: str) -> Dict[str, SensorDataDict]:
        # load ecg and icg data
        # load ecg data
        base_path = self._get_dataset_path("empkins")
        dataset = EmpkinsDataset(base_path, only_labeled=True)
        subset = dataset.get_subset(
            participant=dataset.index.iloc[index]["participant"],
            condition=dataset.index.iloc[index]["condition"],
            phase=dataset.index.iloc[index]["phase"],
        )

        icg_data = subset.icg
        ecg_data = subset.ecg
        if (len(icg_data) == 0) and (len(ecg_data) == 0):
            UserInformation.inform("No data found for this participant, condition, and phase")
            return None

        icg_clean_algo = IcgPreprocessingBandpass()
        ecg_clean_algo = EcgPreprocessingNeurokit()
        ecg_clean_algo.clean(ecg=ecg_data, sampling_rate_hz=dataset.sampling_rate_ecg)
        icg_clean_algo.clean(icg=icg_data, sampling_rate_hz=dataset.sampling_rate_icg)

        sensor_data = pd.concat([ecg_clean_algo.ecg_clean_, icg_clean_algo.icg_clean_], axis=1)
        sensor_data = sensor_data.reset_index(drop=True)

        data = {
            f" Dataset {index}": {
                "sensor_data": sensor_data,
                "sampling_rate_hz": dataset.sampling_rate_icg,
            },
        }
        return data

    def get_name(self) -> str:
        return "EmpkinS Importer"

    def get_selectable_data(self) -> List[str]:
        # get list of every participant and phase
        base_path = self._get_dataset_path("empkins")
        # get list of every participant and phase
        dataset = EmpkinsDataset(base_path)
        list = []
        for i in dataset:
            participant = i.index["participant"][0]
            condition = i.index["condition"][0]
            phase = i.index["phase"][0]
            list.append(f"{participant} {condition} {phase}")

        return list

    def load_annotations(self, index: int) -> Dict[str, pd.DataFrame]:
        # load borders of random selected part of the data for manually labeling
        annotations_dict = dict()
        annotations_dict[f" Dataset {index}"] = {"ICG_ECG_Labels": pd.DataFrame(columns=["pos", "description"])}
        base_path = self._get_dataset_path("empkins")
        dataset = EmpkinsDataset(base_path, only_labeled=True)

        subset = dataset.get_subset(
            participant=dataset.index.iloc[index]["participant"],
            condition=dataset.index.iloc[index]["condition"],
            phase=dataset.index.iloc[index]["phase"],
        )

        ecg_data = subset.ecg
        fs_ecg = subset.sampling_rate_ecg
        ecg_clean_algo = EcgPreprocessingNeurokit()
        ecg_clean_algo.clean(ecg=ecg_data, sampling_rate_hz=fs_ecg)
        ecg_clean = ecg_clean_algo.ecg_clean_

        # run ECG heartbeat extraction
        # load heartbeats to display them in the plot
        heartbeat_algo = HeartbeatSegmentationNeurokit()
        heartbeat_algo.extract(ecg=ecg_clean, sampling_rate_hz=fs_ecg)
        heartbeats = heartbeat_algo.heartbeat_list_

        sample_offset_absolute = subset.labeling_borders["sample_relative"].values[0]

        heartbeat_label_list = []
        for idx, row in heartbeats.iterrows():
            start_sample = row["start_sample"]
            end_sample = row["end_sample"]
            heartbeat_label_list.append(
                pd.DataFrame(
                    {
                        "pos": start_sample,
                        "description": {"heartbeat": f"('start', {idx}, {start_sample+sample_offset_absolute})"},
                    }
                )
            )
            heartbeat_label_list.append(
                pd.DataFrame(
                    {
                        "pos": end_sample,
                        "description": {"heartbeat": f"('end', {idx}, {end_sample+sample_offset_absolute})"},
                    }
                )
            )

        annotations_df = pd.concat(heartbeat_label_list, ignore_index=True)
        annotations_dict[f" Dataset {index}"]["ICG_ECG_Labels"] = annotations_df

        return annotations_dict

    @staticmethod
    def _get_dataset_path(dataset_type: str) -> Path:
        config_path = Path("../../config/config.json")
        config_dict = json.load(config_path.open("r"))
        return Path(config_dict[dataset_type])
