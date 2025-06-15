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

Provides methods to prepare inputs for simulating the `WaTEM/SEDEM <https://github.com/watem-sedem>`_ model, which predicts soil erosion, sediment transport capacity, and sediment delivery to stream networks at the watershed scale. This class currently provides the following feature:

* Converts Digital Elevation Model (DEM) data into the stream files required for the WaTEM/SEDEM model, with the ``river routing = 1`` extension enabled.
* Extends input rasters beyond the model region and fills them with valid values, as WaTEM/SEDEM does not support NoData cells.
* Generates effective upstream drainage polygons for selected dam locations within a stream network.


:class:`OptiDamTool.Network`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Offers methods for establishing hydrological and sedimentation flow connectivity between dams using the stream network. This class currently provides the following feature:

* Identifies connectivity between adjacent upstream and downstream dams.
* Computes the effective upstream drainage area values for selected dam locations within a stream network.

