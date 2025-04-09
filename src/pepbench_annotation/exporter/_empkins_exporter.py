import ast
from pathlib import Path
from typing import Self

import pandas as pd
from mad_gui import BaseExporter
from mad_gui.components.dialogs import UserInformation
from mad_gui.models import GlobalData
from PySide6.QtWidgets import QFileDialog

from pepbench_annotation.importer import EmpkinsImporter
from pepbench_annotation.utils import get_dataset_path


class EmpkinsExporter(BaseExporter):
    TUPLE_MAPPING = {
        "ECG": ("ECG", "Q-wave_onset", None, None),
        "ICG": ("ICG", "B-point", None, None),
        "Artefact": ("Artefact", "Artefact", None, None),
    }

    @classmethod
    def get_name(cls: Self) -> str:
        # This will be shown as string in the dropdown menu of
        # mad_gui.components.dialogs.ExportResultsDialog upon pressing
        # the button "Export data" in the GUI
        return "EmpkinS Exporter"

    def process_data(self, global_data: GlobalData) -> None:
        # This function is called when the user presses the "Export data" button

        name_list = EmpkinsImporter.get_selectable_data(EmpkinsImporter)

        # will be set in the loop
        directory = None

        for plot_name, plot_data in global_data.plot_data.items():
            for _label_name, annotations in plot_data.annotations.items():
                if len(annotations.data) == 0:
                    continue
                # format the dataframe to be able to reload the annotations afterwards
                extracted_number = "".join(filter(str.isdigit, plot_name))
                number = int(extracted_number)
                data = annotations.data[["pos", "description"]]

                # Apply function to split description column
                data = data.rename(columns={"pos": "sample_relative"})
                data[["channel", "label", "heartbeat_id", "sample_absolute"]] = data["description"].apply(
                    lambda x: pd.Series(self.split_tuple(x))
                )
                data = data.sort_values(by=["sample_relative", "heartbeat_id"])

                sample_offset = (data["sample_absolute"] - data["sample_relative"]).dropna().unique()[0].astype(int)

                data_converted = data.assign(heartbeat_id=data["heartbeat_id"].ffill())
                data_converted = data_converted.drop(columns="description")[
                    ["heartbeat_id", "channel", "label", "sample_absolute", "sample_relative"]
                ]
                data_converted = data_converted.assign(sample_absolute=data["sample_relative"] + sample_offset)
                data_converted = data_converted.sort_values(by=["sample_relative", "heartbeat_id"])
                data_converted = data_converted.dropna().astype(
                    {"heartbeat_id": int, "sample_relative": int, "sample_absolute": int}
                )

                datapoint_info = name_list[number].split(" ")
                datapoint_info = [d.lower() for d in datapoint_info]
                base_path = get_dataset_path("empkins")
                # TODO remove rater_02 later
                folder_path = base_path.joinpath(
                    f"data_per_subject/{datapoint_info[0]}/{datapoint_info[1]}/biopac/reference_labels/rater_02"
                )
                directory = QFileDialog().getExistingDirectory(
                    None, "Save .csv results to this folder", str(folder_path)
                )

                for channel in ["ICG", "ECG"]:
                    # filter channel and "heartbeat" from "channel" column
                    channel_combined = ["heartbeat", channel, "Artefact"]
                    data_filtered = data_converted.query(f"channel in {channel_combined}").copy()

                    data_filtered.to_csv(
                        Path(directory).joinpath(f"reference_labels_{'_'.join(datapoint_info)}_{channel.lower()}.csv"),
                        index=False,
                    )

        UserInformation.inform(f"The results were saved to {directory}.")

    def split_tuple(self, value: str) -> tuple:
        parsed = ast.literal_eval(str(value))  # Convert string to tuple
        # parsed = value
        if len(parsed) == 1:
            return self.TUPLE_MAPPING[parsed[0]]
        return ("heartbeat", *parsed)
