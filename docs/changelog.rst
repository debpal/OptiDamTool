===============
Release Notes
===============

Version 0.5.2
---------------

* **Release date:** 24-Nov-2025.

* **Features:** Added a new method to :class:`OptiDamTool.SystemDesign` that enables retrieval of detailed storage dynamics and drainage responses
  for any solution scenario generated during the optimization process.

Version 0.5.1
---------------

* **Release date:** 26-Oct-2025.

* **Features:**

    * Added new objectives in :attr:`OptiDamTool.SystemDesign.mapping_objective_direction` property.
    * Introduced a new mothod in :class:`OptiDamTool.SystemDesign` for retrieving detailed simulation outputs for any solution scenario generated during the optimization process.


Version 0.5.0
---------------

* **Release date:** 02-Oct-2025.

* **Features:**

    * Added :class:`OptiDamTool.SystemDesign` class for optimizing dam systems using multi-objective evolutionary algorithms.
    * Consolidated and streamlined methods for visualizing individual dam features in the :class:`OptiDamTool.Visual` class.
    * Updated documentation regarding new features.


Version 0.4.4
---------------

* **Release date:** 16-Aug-2025.

* **Features:**

    * Added a new class :class:`OptiDamTool.Visual` that provides utilities for visualizing data.
    * Introduced methods for plotting dam locations along streams and overall dam-system statistics.
    * Added methods for plotting annual remaining storage of individual dams and their sediment trapping percentages relative to total sediment inputs.
    * Updated documentation regarding new features.


Version 0.3.4
---------------

* **Release date:** 11-Aug-2025.

* **Features:**

    * Merged separate functions related to saving outputs into the :class:`OptiDamTool.Network` class.
    * Updated documentation regarding new features.


Version 0.3.3
---------------

* **Release date:** 24-Jul-2025.

* **Features:**
  
    * Introduced a new method in the :class:`OptiDamTool.Network` class to generate dam location points and their  
      controlled drainage polygons when dams become inactive during system-wide storage dynamics simulation..
    * Updated documentation regarding new features.



Version 0.3.2
---------------

* **Release date:** 20-Jul-2025.

* **Features:** 

    * Introduced several new methods within the :class:`OptiDamTool.Network` class.
    * Updated documentation regarding new features.


Version 0.2.2
---------------

* **Release date:** 10-Jul-2025.

* **Features:** 

    * Introduced several new methods within the :class:`OptiDamTool.Network` class.
    * Updated documentation regarding new features.


Version 0.2.1
---------------

* **Release date:** 23-Jun-2025.

* **Features:** 

    * Introduced several new methods within the :class:`OptiDamTool.WatemSedem` class.
    * Updated documentation regarding new features.

* **Development status:** Upgraded from Alpha to Beta.


Version 0.1.1
---------------

* **Release date:** 10-Jun-2025.

* **Features:**

    * Introduced new methods within the :class:`OptiDamTool.WatemSedem` and :class:`OptiDamTool.Network` classes.
    * Updated documentation regarding new features.

* **Development status:** Upgraded from Pre-Alpha to Alpha.


Version 0.1.0
---------------

* **Release date:** 06-Jun-2025.

* **Features:** 

    * Introduced a method in the :class:`OptiDamTool.WatemSedem` class.
    * Updated documentation regarding new features.

* **Development status:** Upgraded from Planning to Pre-Alpha.


Version 0.0.2
---------------

* **Release date:** 31-May-2025.

* **Features:** Added :class:`OptiDamTool.Network` class with a method to predict adjacet upstream and downstream dam connectivity.

* **Documentation:** Added a tutorial on how to use the newly introduced features.

* **GitHub Actions Integration:**

    * Linting with `flake8` to enforce PEP8 code formatting.
    * Type checking with `mypy` to verify annotations throughout the codebase.
    * Code testing with `pytest` to ensure code reliability.
    * Test Coverage with **Codecov** to monitor and report test coverage.
    * Automatic documentation builds on **Read the Docs**.


Version 0.0.1
---------------

* **Release date:** 29-May-2025.

* **Features:** Added :class:`OptiDamTool.WatemSedem` class but not functionality has been added.

* **Development status:** Planning.

