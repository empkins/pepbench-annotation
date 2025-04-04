from mad_gui.plot_tools.labels import BaseEventLabel


class BPoint(BaseEventLabel):
    name = "B_point"
    descriptions = {"B_point": None}
    snap_to_min = False
    snap_to_max = False


class QWaveOnset(BaseEventLabel):
    name = "Q_wave_onset"
    descriptions = {"Q_wave_onset": None}
    snap_to_min = False
    snap_to_max = False


class ICGECGLabels(BaseEventLabel):
    snap_to_min = False
    snap_to_max = False
    name = "ICG_ECG_Labels"
    descriptions = {"ECG": None, "ICG": None, "Artefact": None}
