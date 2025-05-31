# OptiDamTool

| <big>Status</big> | <big>Description</big> |
| --- | --- |
| **PyPI**| ![PyPI - Version](https://img.shields.io/pypi/v/OptiDamTool) ![PyPI - Status](https://img.shields.io/pypi/status/OptiDamTool) ![PyPI - Python Version](https://img.shields.io/pypi/pyversions/OptiDamTool) ![PyPI - Wheel](https://img.shields.io/pypi/wheel/OptiDamTool) |
| **GitHub** | ![GitHub commit activity](https://img.shields.io/github/commit-activity/t/debpal/OptiDamTool) ![GitHub last commit](https://img.shields.io/github/last-commit/debpal/OptiDamTool) [![flake8](https://github.com/debpal/OptiDamTool/actions/workflows/linting.yml/badge.svg)](https://github.com/debpal/OptiDamTool/actions/workflows/linting.yml) [![mypy](https://github.com/debpal/OptiDamTool/actions/workflows/typing.yml/badge.svg)](https://github.com/debpal/OptiDamTool/actions/workflows/typing.yml) [![pytest](https://github.com/debpal/OptiDamTool/actions/workflows/testing.yml/badge.svg)](https://github.com/debpal/OptiDamTool/actions/workflows/testing.yml) |
| **Codecov** | [![codecov](https://codecov.io/gh/debpal/OptiDamTool/graph/badge.svg?token=PJOAIRHEW6)](https://codecov.io/gh/debpal/OptiDamTool) |
| **Read** _the_ **Docs** | ![Read the Docs](https://img.shields.io/readthedocs/OptiDamTool) |
| **PePy** | ![Pepy Total Downloads](https://img.shields.io/pepy/dt/OptiDamTool) |
| **License** | ![GitHub License](https://img.shields.io/github/license/debpal/OptiDamTool) |


`OptiDamTool` is a Python package designed for analytics and decision-making in dam operations and water resources management. Conceptualized and released on May 29, 2025, the package offers tools for modeling and analyzing hydrological flow across a network of connected dams.


Leveraging functionalities from the open-source [GeoAnalyze](https://github.com/debpal/GeoAnalyze) package, `OptiDamTool` provides classes that help users prepare inputs for simulating water erosion and sediment transport, and support decision-making in dam network deployment for environmental sustainability.

## Classes

The following classes are included in the package:

- `OptiDamTool.WatemSedem`: Provides methods to prepare inputs for the
[WaTEM/SEDEM](https://github.com/watem-sedem) model, which predicts soil erosion, sediment transport capacity, and sediment delivery to stream networks at a watershed scale. While no methods have been implemented yet, development is currently underway.


- `OptiDamTool.Network`: Offers methods for establishing network connectivity between dams based on stream networks and hydrological flow paths.


## Features

The classes provide the following features:


### *Dam Network*

- Identification of connectivity between adjacent upstream and downstream dams


## Easy Installation

To install, use pip:

```bash
pip install OptiDamTool
```


## Quickstart
A brief example of how to start:

```python
>>> import OptiDamTool
>>> network = OptiDamTool.Network()
```


## Documentation

For detailed information, see the [documentation](https://optidamtool.readthedocs.io/en/latest/).

## Support

If this project has been helpful and you'd like to contribute to its development, consider sponsoring with a coffee! Support will help maintain, improve, and expand this open-source project, ensuring continued valuable tools for the community.


[![Buy Me a Coffee](https://img.shields.io/badge/☕_Buy_me_a_coffee-FFDD00?style=for-the-badge)](https://www.buymeacoffee.com/debasish_pal)


