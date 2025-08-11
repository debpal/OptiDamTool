==============
Installation
==============

The installation of the package is straightforward. It can be installed in an existing ``conda`` environment or in a newly created one.  
To prevent conflicts with other Python packages, it is recommended to create a dedicated ``conda`` environment.

Below are the steps for installing the package using different methods.


Set Up a ``conda`` Environment
------------------------------

You can create a new ``conda`` environment using the Anaconda distribution by following these steps:

.. code-block:: console

    conda create --name <new_env>
    conda activate <new_env>
    conda install pip
    
If you want to install the package in an existing ``conda`` environment, activate it with:

.. code-block:: console

    conda activate <exist_env>


Install from PyPI
-------------------

.. code-block:: console
    
    pip install OptiDamTool



Install from GitHub Repository
------------------------------

To install directly from the GitHub repository, run:

.. code-block:: console

    pip install git+https://github.com/debpal/OptiDamTool.git
    
    
Developer Installation (Editable Mode)
---------------------------------------

For developers who want to modify the source code or contribute to the package, it is recommended to install in editable mode.  
Navigate to your desired directory with your ``conda`` environment activated, and run the following commands.  
This allows you to make changes to the source code, with immediate reflection in the ``conda`` environment without requiring reinstallation.

.. code-block:: console

    pip install build
    git clone https://github.com/debpal/OptiDamTool.git
    cd OptiDamTool
    python -m build
    pip install -e .
    

