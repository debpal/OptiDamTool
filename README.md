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

* Convert Digital Elevation Model (DEM) data into the stream files required for the WaTEM/SEDEM model with the `river routing = 1` extension enabled.
* Extend input rasters beyond the model region and fills NoData cells with valid values, as WaTEM/SEDEM does not support NoData.
* Perform reprojection, clipping, resolution rescaling, and reclassification of rasters.
* Processe open-source [Esri land cover data](https://livingatlas.arcgis.com/landcover/).
* Generate a land management factor raster from land cover inputs.
* Compute the product of soil erodibility and rainfall erosivity factors.
* Convert raster files to the Idrisi raster format, with the `.rst` file extension.
* Generate effective upstream drainage area polygons for selected dam locations within a stream network.


### `OptiDamTool.Network` 
Offers methods for establishing hydrological and sedimentation flow connectivity between dams using the stream network.

* Identify connectivity between adjacent upstream and downstream dams.
* Compute the controlled upstream drainage areas for selected dam locations within a stream network.
* Estimate sediment inflow to dams based on controlled upstream drainage areas.
* Simulate storage dynamics of individual dams in a system due to sedimentation, using a mass balance approach.
* Generate updated dam location points and their corresponding controlled drainage polygons when dams become inactive
  during system-wide storage dynamics simulation.


### `OptiDamTool.Analysis` 
Provides methods for analyzing simulation outputs and generating insights.

* Integrate sediment delivery to stream segments.
* Generate stream shapefiles with comprehensive information of each segment's drainage area and sediment input.
* Summarize total sediment dynamics for the model region.
* Assign a Coordinate Reference System and the default `GTiff` driver to output Idrisi raster files from a WaTEM/SEDEM simulation.

### `OptiDamTool.SystemDesign` 
Provides methods for optimizing dam systems within a watershed using a multi-objective evolutionary computation framework.

* For a fixed number of dams, it determines optimal locations and storage capacities based on annual sediment inflows along watershed drainage pathways.
* Retrieve detailed simulation results for a selected solution scenario.


### `OptiDamTool.Visual` 
Provides methods for visualizing simulation outputs.

* Produces a figure showing sediment inflow percentages to stream segments, relative to the total sediment input across all stream segments.
* Creates a figure showing dam locations along the stream path.
* Produces a figure showing dam system-level statistics, including controlled drainage area, remaining storage, sediment trapped, and sediment released.
* Displays figures illustrating the annual variability of key features for each dam in the system:

    - `Controlled drainage area`: Percentage of the drainage area managed by each dam, relative to the total stream drainage area, evaluated at the start of the simulation year.  
    - `Remaining storage`: Percentage of storage capacity remaining relative to the dam’s initial storage, evaluated at the start of the simulation year.  
    - `Trap efficiency`: Efficiency of sediment trapping expressed as a percentage, evaluated at the start of the simulation year.  
    - `Trapped sediment`: Percentage of sediment retained by the dam, relative to the total sediment input across all stream segments, evaluated at the end of the simulation year.  



The examples below show typical outputs produced by these visualization methods:


<div align="center">
    <img src="https://github.com/debpal/OptiDamTool/raw/main/docs/_static/sediment_inflow_to_stream.png" width="70%">
    <img src="https://github.com/debpal/OptiDamTool/raw/main/docs/_static/dam_location_in_stream.png" width="40%">
    <img src="https://github.com/debpal/OptiDamTool/raw/main/docs/_static/system_statistics.png" width="60%">
    <img src="https://github.com/debpal/OptiDamTool/raw/main/docs/_static/dam_remaining_storage.png" width="60%">
    <img src="https://github.com/debpal/OptiDamTool/raw/main/docs/_static/dam_trap_efficiency.png" width="60%">
    <img src="https://github.com/debpal/OptiDamTool/raw/main/docs/_static/dam_trapped_sediment.png" width="60%">
    <img src="https://github.com/debpal/OptiDamTool/raw/main/docs/_static/dam_drainage_area.png" width="60%">
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


