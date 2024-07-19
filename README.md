# Creator

## Usage

This script provides a series of commands to set up, activate, and manage the Creator's environment.

1. Create the environment:

```bash
conda env create -f environment.yml
```

2. Activate the environment:

```bash
conda activate Creator_env
```

3. Install project dependencies using Poetry:

```bash
poetry install
```

4. Remove the environment:

```bash
conda remove -n Creator_env --all
```
