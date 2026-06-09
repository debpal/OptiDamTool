=============
Introduction
=============


:mod:`OptiDamTool` is a Python package designed for analytics and decision-making in dam operations and water resources management.
Conceptualized and released on May 29, 2025, the package offers tools for modeling and analyzing hydrological flow across a network of connected dams.


Leveraging functionalities from the open-source `GeoAnalyze <https://github.com/debpal/GeoAnalyze>`_ package, :mod:`OptiDamTool` provides classes
that that assist users in preparing inputs for simulating water erosion and sediment transport,
and supports decision-making in dam network deployment aimed at environmental sustainability.


Classes
----------

:class:`OptiDamTool.WatemSedem`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Provides tools to prepare inputs for the `WaTEM/SEDEM <https://github.com/watem-sedem>`_ model, which simulates soil erosion, sediment transport capacity, and sediment delivery to stream networks at the watershed scale. While this class includes built-in methods for generating most required inputs, it is still recommended to consult the ``GeoAnalyze`` documentation for any geospatial operations not covered by its methods.

* Convert Digital Elevation Model (DEM) data into the stream files required for the WaTEM/SEDEM model with the  ``river routing = 1`` extension enabled.
* Extend input rasters beyond the model region and fills NoData cells with valid values, as WaTEM/SEDEM does not support NoData.
* Perform reprojection, clipping, resolution rescaling, and reclassification of rasters.
* Processe open-source `Esri land cover data <https://livingatlas.arcgis.com/landcover/>`_.
* Generate a land management factor raster from land cover inputs.
* Compute the product of soil erodibility and rainfall erosivity factors.
* Convert raster files to the Idrisi raster format, with the ``.rst`` file extension.
* Generate effective upstream drainage area polygons for selected dam locations within a stream network.


:class:`OptiDamTool.Network`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Offers methods for establishing hydrological and sedimentation flow connectivity between dams using the stream network.

* Identifie connectivity between adjacent upstream and downstream dams.
* Compute the effective upstream drainage area values for selected dam locations within a stream network.
* Estimate sediment inflow to dams based on effective upstream drainage areas.
* Simulate storage dynamics of individual dams in a system due to sedimentation, using a mass balance approach.
* Generate updated dam location points and their corresponding controlled drainage polygons when dams become inactive
  during system-wide storage dynamics simulation.


:class:`OptiDamTool.Analysis`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Provides methods for analyzing simulation outputs and generating insights.

* Integrate sediment delivery to stream segments.
* Generate stream shapefiles with comprehensive information of each segment's drainage area and sediment input.
* Summarize total sediment dynamics for the model region.
* Assign a Coordinate Reference System and the default ``GTiff`` driver to output Idrisi raster files from a WaTEM/SEDEM simulation.


:class:`OptiDamTool.SystemDesign`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Provides methods for optimizing dam systems within a watershed using a multi-objective evolutionary computation framework.

* For a fixed number of dams, it determines optimal locations and storage capacities based on annual sediment inflows along watershed drainage pathways.
* Retrieve detailed simulation results for a selected solution scenario.


:class:`OptiDamTool.Visual`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Provides methods for visualizing simulation outputs.

* Produces a figure showing sediment inflow percentages to stream segments, relative to the total sediment input across all stream segments.
* Creates a figure showing dam locations along the stream path.
* Produces a figure showing dam system-level statistics, including controlled drainage area, remaining storage, sediment trapped, and sediment released.
* Displays figures illustrating the annual variability of key features for each dam in the system:

    - **Controlled drainage area**: Percentage of the drainage area managed by each dam, relative to the total stream drainage area, evaluated at the start of the simulation year.  
    - **Remaining storage**: Percentage of storage capacity remaining relative to the dam’s initial storage, evaluated at the start of the simulation year.  
    - **Trap efficiency**: Efficiency of sediment trapping expressed as a percentage, evaluated at the start of the simulation year.  
    - **Trapped sediment**: Percentage of sediment retained by the dam, relative to the total sediment input across all stream segments, evaluated at the end of the simulation year.
* Generates Pareto front visualizations to support the analysis of multi-objective optimization results, including parallel coordinate plots and two-dimensional trade-off projections.

