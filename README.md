# OptiDamTool

| <big>Status</big> | <big>Description</big> |
| --- | --- |
| **PyPI**| ![PyPI - Version](https://img.shields.io/pypi/v/OptiDamTool) ![PyPI - Status](https://img.shields.io/pypi/status/OptiDamTool) ![PyPI - Python Version](https://img.shields.io/pypi/pyversions/OptiDamTool) ![PyPI - Wheel](https://img.shields.io/pypi/wheel/OptiDamTool) |
| **GitHub** | ![GitHub commit activity](https://img.shields.io/github/commit-activity/t/debpal/OptiDamTool) ![GitHub last commit](https://img.shields.io/github/last-commit/debpal/OptiDamTool) [![flake8](https://github.com/debpal/OptiDamTool/actions/workflows/linting.yml/badge.svg)](https://github.com/debpal/OptiDamTool/actions/workflows/linting.yml) [![mypy](https://github.com/debpal/OptiDamTool/actions/workflows/typing.yml/badge.svg)](https://github.com/debpal/OptiDamTool/actions/workflows/typing.yml) [![pytest](https://github.com/debpal/OptiDamTool/actions/workflows/testing.yml/badge.svg)](https://github.com/debpal/OptiDamTool/actions/workflows/testing.yml) |
| **Codecov** | [![codecov](https://codecov.io/gh/debpal/OptiDamTool/graph/badge.svg?token=PJOAIRHEW6)](https://codecov.io/gh/debpal/OptiDamTool) |
| **Read** _the_ **Docs** | ![Read the Docs](https://img.shields.io/readthedocs/OptiDamTool) |
| **PePy** | ![Pepy Total Downloads](https://img.shields.io/pepy/dt/OptiDamTool) |
| **License** | ![GitHub License](https://img.shields.io/github/license/debpal/OptiDamTool) |


`OptiDamTool` is a Python package designed for analytics and decision-making in dam management. Conceptualized and released on May 29, 2025, the package offers tools for modeling and analyzing hydrological flow across a network of connected dams.


Leveraging functionalities from the open-source [GeoAnalyze](https://github.com/debpal/GeoAnalyze) package, `OptiDamTool` provides classes that that assist users in preparing inputs for simulating water erosion and sediment transport, and supports decision-making in dam network deployment aimed at environmental sustainability.

## Classes

### `OptiDamTool.WatemSedem`

Provides tools to prepare inputs for the [WaTEM/SEDEM](https://github.com/watem-sedem) model, which simulates soil erosion, sediment transport capacity, and sediment delivery to stream networks at the watershed scale. While this class includes built-in methods for generating most required inputs, it is still recommended to consult the `GeoAnalyze` documentation for any geospatial operations not covered by its methods.

* Converts Digital Elevation Model (DEM) data into the stream files required for the WaTEM/SEDEM model with the `river routing = 1` extension enabled.
* Extends input rasters beyond the model region and fills NoData cells with valid values, as WaTEM/SEDEM does not support NoData.
* Performs reprojection, clipping, resolution rescaling, and reclassification of rasters.
* Processes open-source [Esri land cover data](https://livingatlas.arcgis.com/landcover/).
* Generates a land management factor raster from land cover inputs.
* Computes the product of soil erodibility and rainfall erosivity factors.
* Converts raster files to the Idrisi raster format, with the `.rst` file extension.
* Generates effective upstream drainage area polygons for selected dam locations within a stream network.


### `OptiDamTool.Network` 
Offers methods for establishing hydrological and sedimentation flow connectivity between dams using the stream network.

* Identifies connectivity between adjacent upstream and downstream dams.
* Computes the effective upstream drainage area values for selected dam locations within a stream network.


### `OptiDamTool.Analysis` 
Provides methods for analyzing simulation outputs and generating insights.

* Integrates sediment delivery to stream segments.
* Generates stream shapefiles with comprehensive information of each segment's drainage area and sediment input.
* Summarizes total sediment dynamics for the model region.
* Assigns a Coordinate Reference System and the default `GTiff` driver to output Idrisi raster files from a WaTEM/SEDEM simulation.


## Easy Installation

To install, use pip:

```bash
pip install OptiDamTool
```


## Quickstart
A brief example of how to start:

```python
>>> import OptiDamTool
>>> watemsedem = OptiDamTool.WatemSedem()
>>> network = OptiDamTool.Network()
```


## Documentation

For detailed information, see the [documentation](https://optidamtool.readthedocs.io/en/latest/).

## Support

If this project has been helpful and you'd like to contribute to its development, consider sponsoring with a coffee! Support will help maintain, improve, and expand this open-source project, ensuring continued valuable tools for the community.


[![Buy Me a Coffee](https://img.shields.io/badge/☕_Buy_me_a_coffee-FFDD00?style=for-the-badge)](https://www.buymeacoffee.com/debasish_pal)


