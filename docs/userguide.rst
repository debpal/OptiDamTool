============
User Guide
============

This guide provides an overview for working with the :mod:`OptiDamTool` package.


Verify Installation
---------------------

To verify the installation, import the package and module and instantiate the classes using the following code.
If no errors are raised, the installation is successful.


.. code-block:: python

    import OptiDamTool
    watemsedem = OptiDamTool.WatemSedem()
    network = OptiDamTool.Network()

    
    
Digital Elevation Model (DEM) to Stream 
---------------------------------------------

To generates the input files required to run the WaTEM/SEDEM model with the
`river routing = 1 <https://watem-sedem.github.io/watem-sedem/model_extensions.html#riverrouting>`_ extension, use the following code.
Refer to the :meth:`OptiDamTool.WatemSedem.dem_to_stream` method for more details on the output.
A sample DEM raster file available in the `data <https://github.com/debpal/OptiDamTool/tree/main/tests/data>`_ directory for testing purposes.

.. code-block:: python

    watemsedem.dem_to_stream(
        dem_file=r"C:\users\username\data\dem.tif",
        flwacc_percent=1,
        folder_path=r"C:\users\username\output_folder",
    )
    

    
Adjacent Connectivity Between Dams
-----------------------------------------

To determine the adjacent upstream and downstream connectivity between dams based on a stream network, a stream shapefile is required.
This shapefile must contain a column representing a unique identifier for each stream segment.

Only one dam can be deployed per stream segment, and the dam is identified by the corresponding stream segment’s unique identifier.
The specified stream segment identifiers are used to designate dam deployment locations.

A sample stream shapefile is available in the  `data <https://github.com/debpal/OptiDamTool/tree/main/tests/data>`_ directory.
The following code generates dictionaries representing the adjacent upstream and downstream connectivity of dams based on the stream network.
Refer to the :meth:`OptiDamTool.Network.connectivity_adjacent` method for more details on the output.


.. code-block:: python

    network.connectivity_adjacent(
        stream_file=r"C:\users\username\data\stream.shp",
        stream_column='flw_id',
        dam_list=[21, 22, 5, 31, 17, 24, 27, 2, 13, 1]
    )
   
    
    
 