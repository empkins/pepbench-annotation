# pepbench-annotation

MaD-GUI extension to manually annotate data for the pepbench project.

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


