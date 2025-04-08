# pepbench-annotation

MaD-GUI extension to manually annotate data for the [`pepbench`](https://github.com/empkins/pepbench) project.

## Installation

First install a supported Python version (3.10 or higher) and then install the package using `pip`.

```bash
pip install pepbench-annotation
```

### Installing from GitHub

If you want to install the latest version from GitHub, you can use the following command:

```bash
pip install "git+https://github.com/empkins/pepbench-annotation.git"
```

If you run into problems, clone the repository and install the package locally.

```bash
git clone https://github.com/empkins/pepbench-annotation.git
cd pepbench-annotation
pip install .
```


### For Developers
Install Python >=3.10 and [uv](https://docs.astral.sh/uv/getting-started/installation/).
Then run the commands below to install [poethepoet](https://poethepoet.natn.io), get the latest source,
and install the dependencies:

```bash
git clone https://github.com/empkins/pepbench-annotation.git
uv tool install poethepoet
uv sync --all-extras --dev
```

## Usage

All you need to do is start the GUI from the `start_gui.py` file. Afterwards, select the 
dataset you want to annotate (EmpkinS or Guardian) and select the first datapoint.

This will load the raw data (ECG and ICG) and display it in the GUI in one joint plot.
You can then use the GUI to annotate the data.

Annotations can be set by pressing the `A` key to switch from annotating *regions* (the default in the MaD-GUI, 
not needed here) to annotating single *events*. Afterwards, click in the plot to set the annotation and select the
type of annotation (ECG Q-peak, ICG, B-point, or Artefact) in the dropdown menu.

If you are done annotating, you can save the annotations by clicking on "Export" and selecting the correct 
exporter for the dataset you are using (EmpkinS or Guardian).

Other useful commands:
* `Q` - Move the plot to the left (by 2/3 of the screen)
* `W` - Move the plot to the right (by 2/3 of the screen)
* `E` - Edit existing annotations (by clicking on them)
* `R` - Remove existing annotations (by clicking on them)
