import json
from pathlib import Path

import pandas as pd
from biopsykit.signals.ecg.preprocessing import EcgPreprocessingNeurokit
from biopsykit.signals.ecg.segmentation import HeartbeatSegmentationNeurokit
from biopsykit.signals.icg.preprocessing import IcgPreprocessingBandpass


from mad_gui.components.dialogs import UserInformation
from mad_gui.plugins.base import BaseDataImporter, SensorDataDict
from typing import Dict, List

from pepbench.datasets import GuardianDataset


class ICGImporter(BaseDataImporter):
    def load_sensor_data(self, index: str) -> Dict[str, SensorDataDict]:
        # load icg data
        base_path = self._get_dataset_path("guardian")
        dataset = GuardianDataset(base_path, only_labeled=True)
        subset = dataset.get_subset(
            participant=dataset.index.iloc[index]["participant"], phase=dataset.index.iloc[index]["phase"]
        )
        icg_data = subset.icg
        if len(icg_data) == 0:
            UserInformation.inform("No data found for this participant and phase")
            return None

        icg_clean_algo = IcgPreprocessingBandpass()
        icg_clean_algo.clean(icg=icg_data, sampling_rate_hz=dataset.sampling_rate_icg)

        data = {
            f" Dataset {index}": {
                "sensor_data": icg_clean_algo.icg_clean_.reset_index(drop=True),
                "sampling_rate_hz": dataset.sampling_rate_icg,
            }
        }
        return data

    def get_name(self) -> str:
        return "ICG Importer"

    def get_selectable_data(self) -> List[str]:
        # get list of every participant and phase
        base_path = self._get_dataset_path("guardian")
        # get list of every participant and phase
        dataset = GuardianDataset(base_path)
        list = []
        for i in dataset:
            participant = i.index["participant"][0]
            phase = i.index["phase"][0]
            list.append(f"{participant} {phase}")

        return list

    def load_annotations(self, index: int) -> Dict[str, pd.DataFrame]:
        # load borders of the random selected part of the data for manually labeling
        annotations_dict = dict()
        annotations_dict[f" Dataset {index}"] = {"ICG_ECG_Labels": pd.DataFrame(columns=["pos", "description"])}

        base_path = self._get_dataset_path("guardian")
        dataset = GuardianDataset(base_path, only_labeled=True)
        subset = dataset.get_subset(
            participant=dataset.index.iloc[index]["participant"], phase=dataset.index.iloc[index]["phase"]
        )

        ecg_data = subset.ecg
        fs_ecg = subset.sampling_rate_ecg
        ecg_clean_algo = EcgPreprocessingNeurokit()
        ecg_clean_algo.clean(ecg=ecg_data, sampling_rate_hz=fs_ecg)
        ecg_clean = ecg_clean_algo.ecg_clean_

        # run ECG heartbeat extraction
        heartbeat_algo = HeartBeatExtraction()
        heartbeat_algo.extract(ecg_clean=ecg_clean, sampling_rate_hz=fs_ecg)
        heartbeats = heartbeat_algo.heartbeat_list_

        # run ECG heartbeat extraction
        # load heartbeats to display them in the plot
        heartbeat_algo = HeartbeatSegmentationNeurokit()
        heartbeat_algo.extract(ecg=ecg_clean, sampling_rate_hz=fs_ecg)
        heartbeats = heartbeat_algo.heartbeat_list_

        heartbeat_label_list = []
        for idx, row in heartbeats.iterrows():
            start_sample = row["start_sample"]
            end_sample = row["end_sample"]
            heartbeat_label_list.append(pd.DataFrame({"pos": start_sample, "description": {"heartbeat": "start"}}))
            heartbeat_label_list.append(pd.DataFrame({"pos": end_sample, "description": {"heartbeat": "end"}}))

        annotations_df = pd.concat(heartbeat_label_list, ignore_index=True)
        annotations_dict[f" Dataset {index}"]["ICG_ECG_Labels"] = annotations_df

        return annotations_dict

    @staticmethod
    def _get_dataset_path(dataset_type: str) -> Path:
        config_path = Path("../../config/config.json")
        config_dict = json.load(config_path.open("r"))
        return Path(config_dict[dataset_type])
