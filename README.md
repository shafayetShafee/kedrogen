# kedrogen

[![PyPI](https://img.shields.io/pypi/v/kedrogen.svg)](https://pypi.org/project/kedrogen/) ![Python Versions](https://img.shields.io/pypi/pyversions/kedrogen) ![License](https://img.shields.io/pypi/l/kedrogen) [![Build](https://github.com/shafayetShafee/kedrogen/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/shafayetShafee/kedrogen/actions/workflows/ci-cd.yml) [![Documentation Status](https://readthedocs.org/projects/kedrogen/badge/?version=latest)](https://kedrogen.readthedocs.io/en/latest/?badge=latest)
[![Code style: ruff-format](https://img.shields.io/badge/code%20style-ruff_format-6340ac.svg)](https://github.com/astral-sh/ruff) [![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

A simple CLI command that generate a Kedro project from a cookiecutter template in the current directory.

## Installation

```console
pip install kedrogen
```
  
## Usage

```console
$ kedrogen [OPTIONS] TEMPLATE
```

**Arguments**:

* `TEMPLATE_PATH`: Specify the template to use when creating the project.
This can be the path to a local directory, a URL to a remote VCS repository supported
by `cookiecutter` or path to either a local or remote zip file.
  [required]

**Options**:

* `-c, --checkout TEXT`: The branch, tag or commit ID to checkout after clone.
* `-d, --directory TEXT`: An optional directory inside the repository to use as the template, that is,
the directory within the repository where cookiecutter.json lives.
* `-p, --password TEXT`: The password to use when extracting a password protected zipfile
* `-vv, --verbose`: Enable verbose output to show detailed progress and debug information.
* `-q, --quiet`: Suppress all non-error messages.
* `-v, --version`: Show the version and exit.
* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `-h, --help`: Show this message and exit.


## Contributing

Interested in contributing? Check out the contributing guidelines. Please note that this project is released with a Code of Conduct. By contributing to this project, you agree to abide by its terms.

## License

`kedrogen` was created by Shafayet Khan Shafee. It is licensed under the terms of the MIT license.
