=============
Introduction
=============


:mod:`OptiDamTool` is a Python package designed for analytics and decision-making in dam operations and water resources management.
Conceptualized and released on May 29, 2025, the package offers tools for modeling and analyzing hydrological flow across a network of connected dams.


Leveraging functionalities from the open-source `GeoAnalyze <https://github.com/debpal/GeoAnalyze>`_ package, :mod:`OptiDamTool` provides classes
that help users prepare inputs for simulating water erosion and sediment transport, and support decision-making in dam network deployment for environmental sustainability.


Classes
----------


The following classes are included in the package:

- :class:`OptiDamTool.WatemSedem`: Provides methods to prepare inputs for the `WaTEM/SEDEM <https://github.com/watem-sedem>`_ model, which predicts soil erosion, sediment transport capacity, and sediment delivery to stream networks at a watershed scale. While no methods have been implemented yet, development is currently underway.

..

- :class:`OptiDamTool.Network`: Offers methods for establishing network connectivity between dams based on stream networks and hydrological flow paths.



Features
---------------------
The classes provide the following features:


*Dam Network*
^^^^^^^^^^^^^^^^^^

- Identification of connectivity between adjacent upstream and downstream dams

