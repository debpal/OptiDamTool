# OptiDamTool


![PyPI - Version](https://img.shields.io/pypi/v/OptiDamTool) ![PyPI - Python Version](https://img.shields.io/pypi/pyversions/OptiDamTool) ![PyPI - Status](https://img.shields.io/pypi/status/OptiDamTool) ![PyPI - Format](https://img.shields.io/pypi/format/OptiDamTool)

![GitHub last commit](https://img.shields.io/github/last-commit/debpal/OptiDamTool) ![GitHub commit activity](https://img.shields.io/github/commit-activity/t/debpal/OptiDamTool)
 [![codecov](https://codecov.io/gh/debpal/OptiDamTool/graph/badge.svg?token=PJOAIRHEW6)](https://codecov.io/gh/debpal/OptiDamTool) 

[![flake8](https://github.com/debpal/OptiDamTool/actions/workflows/linting.yml/badge.svg)](https://github.com/debpal/OptiDamTool/actions/workflows/linting.yml) [![mypy](https://github.com/debpal/OptiDamTool/actions/workflows/typing.yml/badge.svg)](https://github.com/debpal/OptiDamTool/actions/workflows/typing.yml) [![pytest](https://github.com/debpal/OptiDamTool/actions/workflows/testing.yml/badge.svg)](https://github.com/debpal/OptiDamTool/actions/workflows/testing.yml) 
![Read the Docs](https://img.shields.io/readthedocs/OptiDamTool)


![GitHub Release Date](https://img.shields.io/github/release-date/debpal/OptiDamTool)
![GitHub Created At](https://img.shields.io/github/created-at/debpal/OptiDamTool)


![Pepy Total Downloads](https://img.shields.io/pepy/dt/OptiDamTool) 
![PyPI - License](https://img.shields.io/pypi/l/OptiDamTool) 


## About

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
* Computes the controlled upstream drainage areas for selected dam locations within a stream network.
* Estimates sediment inflow to dams based on controlled upstream drainage areas.
* Simulates storage dynamics of individual dams in a system due to sedimentation, using a mass balance approach.
* Generates updated dam location points and their corresponding controlled drainage polygons when dams become inactive
  during system-wide storage dynamics simulation.


### `OptiDamTool.Analysis` 
Provides methods for analyzing simulation outputs and generating insights.

* Integrates sediment delivery to stream segments.
* Generates stream shapefiles with comprehensive information of each segment's drainage area and sediment input.
* Summarizes total sediment dynamics for the model region.
* Assigns a Coordinate Reference System and the default `GTiff` driver to output Idrisi raster files from a WaTEM/SEDEM simulation.

### `OptiDamTool.SystemDesign` 
Provides methods for optimizing dam systems within a watershed using a multi-objective evolutionary computation framework.

* Optimizes dam locations and storage volumes based on annual sediment inflow through watershed drainage pathways.


### `OptiDamTool.Visual` 
Provides methods for visualizing simulation outputs.

* Produces a figure showing sediment inflow percentages to stream segments, relative to the total sediment input across all stream segments.
* Creates a figure showing dam locations along the stream path.
* Displays figures showing annual remaining storage and trapping efficiency of each dam at the beginning of the year.
* Generates a figure showing the annual sediment trapping percentage by each dam in the system, relative to the total sediment input across all stream segments during the year.
* Produces a figure showing dam system-level statistics, including controlled drainage area, remaining storage, sediment trapped, and sediment released.



The examples below show typical outputs produced by these visualization methods:


<div align="center">
    <img src="https://github.com/debpal/OptiDamTool/raw/main/docs/_static/sediment_inflow_to_stream.png" width="70%">
    <img src="https://github.com/debpal/OptiDamTool/raw/main/docs/_static/dam_location_in_stream.png" width="40%">
    <img src="https://github.com/debpal/OptiDamTool/raw/main/docs/_static/dam_remaining_storage.png" width="60%">
    <img src="https://github.com/debpal/OptiDamTool/raw/main/docs/_static/dam_trap_efficiency.png" width="60%">
    <img src="https://github.com/debpal/OptiDamTool/raw/main/docs/_static/dam_trapped_sediment.png" width="60%">
    <img src="https://github.com/debpal/OptiDamTool/raw/main/docs/_static/system_statistics.png" width="60%">
</div>



## Installation

To install, use pip:

```bash
pip install OptiDamTool
```


## Quickstart
A brief example of how to start:

```python
import OptiDamTool
watem_sedem = OptiDamTool.WatemSedem()
network = OptiDamTool.Network()
```


## Documentation

For detailed information, see the [documentation](https://optidamtool.readthedocs.io/en/latest/).

## Support

If this project has been helpful and you'd like to contribute to its development, consider sponsoring with a coffee! Support will help maintain, improve, and expand this open-source project, ensuring continued valuable tools for the community.


[![Buy Me a Coffee](https://img.shields.io/badge/☕_Buy_me_a_coffee-FFDD00?style=for-the-badge)](https://www.buymeacoffee.com/debasish_pal)


