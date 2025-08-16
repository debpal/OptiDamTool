===============
Release Notes
===============

Version 0.4.4
---------------

* **Release date:** 16-Aug-2025.

* **Features:**

    * Added a new class :class:`OptiDamTool.Visual` that provides utilities for visualizing data.
    * Introduced methods for plotting dam locations along streams and overall dam-system statistics.
    * Added methods for plotting annual remaining storage of individual dams and their sediment trapping percentages relative to total sediment inputs.

* **Documentation:** Updated to include details of the new visualization features.


Version 0.3.4
---------------

* **Release date:** 11-Aug-2025.

* **Features:** Merged separate functions related to saving outputs into the corresponding storage dynamics methods: :meth:`OptiDamTool.Network.storage_dynamics_detailed` and :meth:`OptiDamTool.Network.storage_dynamics_lite`.

* **Documentation:** Updated documentation regarding these features.


Version 0.3.3
---------------

* **Release date:** 24-Jul-2025.

* **Features:** Introduced a new method in the :class:`OptiDamTool.Network` class to generate dam location points and their  
  controlled drainage polygons when dams become inactive during system-wide storage dynamics simulation.

* **Documentation:** Added a tutorial demonstrating how to use the newly introduced feature.


Version 0.3.2
---------------

* **Release date:** 20-Jul-2025.

* **Features:** Introduced several new methods within the :class:`OptiDamTool.Network` class.

* **Documentation:** Added a tutorial demonstrating how to use the newly introduced features.


Version 0.2.2
---------------

* **Release date:** 10-Jul-2025.

* **Features:** Introduced several new methods within the :class:`OptiDamTool.Network` class.

* **Documentation:** Added a tutorial demonstrating how to use the newly introduced features.


Version 0.2.1
---------------

* **Release date:** 23-Jun-2025.

* **Features:** Introduced several new methods within the :class:`OptiDamTool.WatemSedem` class.

* **Documentation:** Added a tutorial demonstrating how to use the newly introduced features.

* **Development status:** Upgraded from Alpha to Beta.


Version 0.1.1
---------------

* **Release date:** 10-Jun-2025.

* **Features:** Introduced new methods within the :class:`OptiDamTool.WatemSedem` and :class:`OptiDamTool.Network` classes.

* **Documentation:** Added a tutorial detailing the usage of the newly introduced features.

* **Development status:** Upgraded from Pre-Alpha to Alpha.


Version 0.1.0
---------------

* **Release date:** 06-Jun-2025.

* **Features:** Introduced a method in the :class:`OptiDamTool.WatemSedem` class.

* **Documentation:** Added a tutorial on how to use the newly introduced feature.

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

