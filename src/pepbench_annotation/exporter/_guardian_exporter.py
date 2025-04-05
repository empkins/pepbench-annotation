import ast

import pandas as pd


from mad_gui import BaseExporter
from mad_gui.components.dialogs import UserInformation
from mad_gui.models import GlobalData
from pathlib import Path
from PySide6.QtWidgets import QFileDialog

from pepbench_annotation.importer import GuardianImporter


class GuardianExporter(BaseExporter):
    TUPLE_MAPPING = {
        "ECG": ("ECG", "Q-wave_onset", None, None),
        "ICG": ("ICG", "B-point", None, None),
        "Artefact": ("Artefact", "Artefact", None, None),
    }

    @classmethod
    def get_name(cls) -> str:
        # This will be shown as string in the dropdown menu of
        # mad_gui.components.dialogs.ExportResultsDialog upon pressing
        # the button "Export data" in the GUI
        return "Guardian Exporter"

    def process_data(self, global_data: GlobalData):
        # This function is called when the user presses the "Export data" button

        directory = QFileDialog().getExistingDirectory(
            None, "Save .csv results to this folder", str(Path(global_data.data_file).parent)
        )
        name_list = GuardianImporter.get_selectable_data(GuardianImporter)

        for plot_name, plot_data in global_data.plot_data.items():
            for label_name, annotations in plot_data.annotations.items():
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

                for channel in ["ICG", "ECG"]:
                    # filter channel and "heartbeat" from "channel" column
                    channel_combined = ["heartbeat", channel, "Artefact"]
                    data_filtered = data_converted.query(f"channel in {channel_combined}").copy()

                    data_filtered.to_csv(
                        Path(directory).joinpath(
                            f"{name_list[number].replace(' ', '_')}_{channel}_reference_labels.csv"
                        ),
                        index=False,
                    )

    def split_tuple(self, value):
        parsed = ast.literal_eval(str(value))  # Convert string to tuple
        # parsed = value
        if len(parsed) == 1:
            return self.TUPLE_MAPPING[parsed[0]]
        else:
            return ("heartbeat", *parsed)

        UserInformation.inform(f"The results were saved to {directory}.")
