NOTE: This repository and the associated Python package are deprecated.
As of hermes v0.10, the Python/pyproject.toml plugin is part of the hermes codebase.
It can be configured by adding the following code to your `hermes.toml` file:

``` toml
[harvest]
sources = [ "toml" ]
```

No further installation is required.
Please remove any `pip install` calls for `hermes-plugin-python` or `git+https://github.com/softwarepub/hermes-plugin-python` from your publication workflow.

# Hermes harvest plugin for .toml files
This plugin enables the harvesting of metadata stored in the .toml file of the project. It is configured to automatically harvest from "pyproject.toml". Although it can be used for every .toml file it uses the fields commonly used in .toml files for python.


## Authors

- [@led02](https://www.github.com/led02)
- [@notactuallyfinn](https://www.github.com/notactuallyfinn)


## Related

The hermes project

[Github repository](https://github.com/hermes-hmc/hermes)

The hermes harvest plugin for git

[Github repository](https://github.com/hermes-hmc/hermes-git)
## Run Locally

Clone Hermes project

```bash
  git clone https://github.com/hermes-hmc/hermes.git
```

Go to the project directory

```bash
  cd your_other_folder
```

Make a python package out of it

```bash
  pip install .
```

Clone the project

```bash
  git clone https://github.com/hermes-hmc/hermes-python.git
```

Go to the project directory

```bash
  cd your_folder
```

Make a python package out of it

```bash
  pip install .
```

Go to the project folder you want to harvest

```bash
  cd your_project_to_harvest
```

Controll that you have a file named "hermes.toml" in your project with the following content.
```
  [harvest]
  sources = ["cff", "toml"]

  [deposit.invenio_rdm]
  site_url = "https://sandbox.zenodo.org"
  access_right = "open"
```

Run harvest command

```bash
  hermes harvest
```

![Logo](https://docs.software-metadata.pub/en/latest/_static/hermes-visual-blue.svg)

