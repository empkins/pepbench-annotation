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

All you need to do is start the GUI from the `start_gui.py` file. Afterwards, click on "Load from Plugin" and select the 
importer plugin for the dataset you want to annotate ("EmpkinS Importer" or "Guardian Importer"). The first available 
datapoint for annotation is then automatically selected. 

This will load the raw data (ECG and ICG) and display it in the GUI in one joint plot. You can then use the GUI to 
annotate the data. To zoom in on the data, you can use the mouse wheel or trackpad. To only zoom in on one axis
(x or y, respectively), and keep the other axis fixed, hover over the axis you want to zoom in on and then zoom in 
using the mouse wheel or trackpad. It is very recommended to zoom in on the data for proper annotation, and to have a 
maximum of 5-6 heartbeats being displayed at once.

Annotations can be set by pressing the `A` key (or by clicking on the "Add Annotation" button in the GUI). By default,
the MaD-GUI is set to annotate *regions* with start and end borders (not needed here). To only annotate *single events*,
hold the `Ctrl` key (on Windows) or `Cmd` key (on Mac) while clicking into the plot where you want to set the 
annotation. Afterwards, you can select the annotation type (ECG Q-peak, ICG, B-point, or Artefact) from the popup menu.

If you are done annotating with one datapoint, you can save the annotations by clicking on "Export Data" and 
selecting the correct exporter for the dataset you are using ("EmpkinS Exporter" or "Guardian Exporter"). The 
annotations will be saved as csv files in the respective subfolders (automatically selected by the GUI).

Other useful commands:
* `Q` - Move the plot to the left (by 2/3 of the screen)
* `W` - Move the plot to the right (by 2/3 of the screen)
* `E` - Edit existing annotations (by clicking on them)
* `R` - Remove existing annotations (by clicking on them)
