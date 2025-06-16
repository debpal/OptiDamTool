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


.. _dem_to_stream:
    
DEM to Stream 
-------------------

To generate the input files required to run the WaTEM/SEDEM model with the  
`river routing = 1 <https://watem-sedem.github.io/watem-sedem/model_extensions.html#riverrouting>`_ extension,  
refer to the :meth:`OptiDamTool.WatemSedem.dem_to_stream` method for more details on the output.  
A sample Digital Elevation Model (DEM) raster file is available in the  
`data <https://github.com/debpal/OptiDamTool/tree/main/tests/data>`_ directory for testing purposes.


.. code-block:: python

    watemsedem.dem_to_stream(
        dem_file=r"C:\users\username\data\dem.tif",
        flwacc_percent=1,
        folder_path=r"C:\users\username\output_folder"
    )
    

.. _model_region_extension:

Model Region Extension 
--------------------------

Since WaTEM/SEDEM does not support NoData cells, rasters must be extended beyond the original model region to include a buffer area.  
A raster that covers the model region, typically the DEM raster, is used to create an extended region raster that includes the desired buffer zone.

.. code-block:: python
    
    # extended region raster with DEM boundary polygons
    watemsedem.model_region_extension(
        region_file=r"C:\users\username\data\dem.tif",
        buffer_distance=1500,
        resolution=30,
        folder_path=r"C:\users\username\output_folder"
    )
    

Raster Extension without NoData Region 
------------------------------------------

Using the ``region_buffer.tif`` raster generated in the :ref:`model_region_extension` section,  
the stream raster produced in the :ref:`dem_to_stream` section is extended, and NoData cells are filled with valid values.

.. code-block:: python
    
    # stream rater extension with extended model region
    watemsedem.raster_extension_without_nodata(
        input_file=r"C:\users\username\output_folder\stream_lines.tif",
        fill_value=0,
        region_file=r"C:\users\username\output_folder\region_buffer.tif",
        output_file=r"C:\users\username\output_folder\stream_buffer.tif"
    )
    
    
Constant Raster without NoData Region 
------------------------------------------

A constant raster, such as the `erosion control factor <https://watem-sedem.github.io/watem-sedem/watem-sedem.html#p-factor>`_,  
is required for small regions when running WaTEM/SEDEM.  
Using the ``region_buffer.tif`` raster generated in the :ref:`model_region_extension` section,  
a constant raster can be created efficiently as shown below:

.. code-block:: python
    
    # erosion control factor raster
    watemsedem.output = watemsedem.raster_constant_without_nodata(
        input_file=r"C:\users\username\output_folder\region_buffer.tif",
        constant_value=1,
        fill_nodata=0,
        output_file=r"C:\users\username\output_folder\p_buffer.tif",
        dtype='float32'
    )

    
Adjacent Connectivity Between Dams
-----------------------------------------

To determine the adjacent upstream and downstream connectivity between dams based on a stream network, a stream shapefile is required.  
This shapefile must contain a column representing a unique identifier for each stream segment.

Only one dam can be deployed per stream segment, and the dam is identified by the corresponding stream segment’s unique identifier.  
The specified stream segment identifiers are used to designate dam deployment locations.

A sample stream shapefile is available in the  
`data <https://github.com/debpal/OptiDamTool/tree/main/tests/data>`_ directory.  
The examples below generate dictionaries representing the adjacent upstream and downstream connectivity of dams based on the stream network.  
A value of -1 indicates no downstream connectivity, while an empty list indicates no upstream connectivity.


.. code-block:: python
    
    # adjacent downstream connectivity
    network.connectivity_adjacent_downstream(
        stream_file=r"C:\users\username\data\stream.shp",
        stream_col='ws_id',
        dam_list=[21, 22, 5, 31, 17, 24, 27, 2, 13, 1]
    )
    
    # adjacent upstream connectivity
    network.connectivity_adjacent_downstream(
        stream_file=r"C:\users\username\data\stream.shp",
        stream_col='ws_id',
        dam_list=[21, 22, 5, 31, 17, 24, 27, 2, 13, 1]
    )
    
    
Effective Drainage Area of Dams
-----------------------------------------

When working with a dam system within a stream network, the effective upstream drainage areas  
for each dam are dynamically influenced by their specific locations.  
The following methods calculate these areas and generate both a dictionary of values and a polygon shapefile representing the upstream drainage areas.


.. code-block:: python
    
    # dictionary of dams' effective upstream drainage area
    network.effective_upstream_drainage_area(
        stream_file=r"C:\users\username\data\stream.shp",
        stream_col='ws_id',
        info_file=r"C:\users\username\data\stream_information.txt",
        dam_list=[21, 22, 5, 31, 17, 24, 27, 2, 13, 1]
    )    
    
    # GeoDataFrame of dams' effective upstream drainage polygons
    watemsedem.dam_effective_drainage_area(
        flwdir_file=r"C:\users\username\flwdir.shp",
        location_file=r"C:\users\username\subbasin_drainage_points.shp",
        location_col='ws_id',
        dam_list=[21, 22, 5, 31, 17, 24, 27, 2, 13, 1],
        folder_path=r"C:\users\username\output_folder"
    )    
    
 