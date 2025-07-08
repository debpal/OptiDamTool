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
    analysis = OptiDamTool.Analysis()


.. _ref_dem_to_stream:
    
DEM to Stream 
-------------------

To generate the input files required to run the WaTEM/SEDEM model with the  
`river routing = 1 <https://watem-sedem.github.io/watem-sedem/model_extensions.html#riverrouting>`_ extension,  
refer to the :meth:`OptiDamTool.WatemSedem.dem_to_stream` method for more details on the output.  
A sample Digital Elevation Model (DEM) raster file is available in the  
`data <https://github.com/debpal/OptiDamTool/tree/main/tests/data>`_ directory for testing purposes.


.. code-block:: python

    watemsedem.dem_to_stream(
        dem_file=r"C:\users\username\input_data\dem.tif",
        flwacc_percent=1,
        folder_path=r"C:\users\username\output_folder"
    )
    

.. _ref_model_region_extension:

Model Region Extension 
--------------------------

Since WaTEM/SEDEM does not support NoData cells, rasters must be extended beyond the original model region to include a buffer area.  
A raster that covers the model region, typically the DEM raster, is used to create an extended region raster that includes the desired buffer zone.

.. code-block:: python
    
    # extended region raster with DEM boundary polygons
    watemsedem.model_region_extension(
        dem_file=r"C:\users\username\input_folder\dem.tif",
        buffer_units=50,
        folder_path=r"C:\users\username\output_folder"
    )
    

Raster Extension without NoData Region 
------------------------------------------

Using the ``region_buffer.tif`` raster generated in the :ref:`ref_model_region_extension` section,  
input rasters for WaTEM/SEDEM, such as the stream raster produced in the :ref:`ref_dem_to_stream` section, are spatially extended.
During this process, NoData areas are replaced with a specified fill value, resulting in a continuous raster suitable for further analysis.

.. code-block:: python
    
    # stream raster extension with extended model region
    watemsedem.raster_extension(
        input_file=r"C:\users\username\output_folder\stream_lines.tif",
        fill_value=0,
        region_file=r"C:\users\username\output_folder\region_buffer.tif",
        output_file=r"C:\users\username\output_folder\stream_buffer.tif"
    )

A constant raster, such as the `erosion control factor <https://watem-sedem.github.io/watem-sedem/watem-sedem.html#p-factor>`_,  
is required for small regions when running WaTEM/SEDEM.  
Using the ``region.tif`` and ``region_buffer.tif`` rasters generated in the :ref:`ref_model_region_extension` section,  
a constant-value raster can be created efficiently, as shown below:

.. code-block:: python
    
    # erosion control factor raster
    watemsedem.raster_constant_extension(
        input_file=r"C:\users\username\output_folder\region.tif",
        constant_value=1,
        region_file=r"C:\users\username\output_folder\region_buffer.tif",
        output_file=r"C:\users\username\output_folder\RUSEL_P_buffer.tif",
        fill_value=0,
        dtype='float32'
    )
    
    
Raster Spatial Analysis
-------------------------------

For focused spatial analysis, extracting a specific region from a large raster is often necessary.
This function clips a raster using a rectangular bounding box derived from the total bounds
of an input shapefile. If required, the shapefile’s Coordinate Reference System (CRS) is automatically transformed
to match the CRS of the raster.


.. code-block:: python
    
    watemsedem.raster_clipping_by_bounding_box(
        input_file=r"C:\users\username\input_folder\land_cover_ESRI.tif",
        shape_file=r"C:\users\username\output_folder\region_buffer.tif",
        output_file=r"C:\users\username\output_folder\land_cover_region.tif",
        dtype='int16'
    )

After clipping, the output raster must be reprojected, clipped again, and rescaled in resolution
to align with the model region. The input shapefile's CRS and spatial extent are used
for reprojection and spatial clipping. A mask raster, which shares the same extent as the shapefile,
is used to rescale the resolution of the reprojected and clipped raster.


.. code-block:: python
    
    watemsedem.raster_reproject_clipping_rescaling(
        input_file=r"C:\users\username\output_folder\land_cover_region.tif",
        resampling_method='nearest',
        shape_file=r"C:\users\username\output_folder\region.shp",
        mask_file=r"C:\users\username\output_folder\region.tif",
        output_file=r"C:\users\username\output_folder\land_cover_unprocessed.tif"
    )
    
    
Land Cover Processing
-------------------------------

To create land cover and management factor rasters required by WaTEM/SEDEM,
use the following codes and refer to methods :meth:`OptiDamTool.WatemSedem.land_cover_esri`
and :meth:`OptiDamTool.WatemSedem.land_management_factor` for more details.

.. code-block:: python
    
    # land cover raster 
    watemsedem.land_cover_esri(
        lc_file=r"C:\users\username\output_folder\land_cover_unprocessed.tif",
        stream_file=r"C:\users\username\output_folder\stream_lines.shp",
        folder_path=r"C:\users\username\output_folder"
    )
    
    # land management factor
    watemsedem.land_cover_esri(
        lc_file=r"C:\users\username\output_folder\land_cover_unprocessed.tif",
        stream_file=r"C:\users\username\output_folder\stream_lines.shp",
        output_file=r"C:\users\username\output_folder\RUSLE_C.tif"
    )
    
    
Product of Soil Erodibility and Rainfall Erosivity Factors
--------------------------------------------------------------------

WaTEM/SEDEM uses the product of the Soil Erodibility (K) and Rainfall Erosivity (R) factors
when these values vary spatially across a large area. The multiplication is normalized by setting
the value of R to 1 where necessary. Refer to the method :meth:`OptiDamTool.WatemSedem.rusle_kr` for more details.

.. code-block:: python
    
    watemsedem.rusle_kr(
        k_file=r"C:\users\username\input_data\RUSLE_K.tif",
        r_file=r"C:\users\username\input_data\RUSLE_R.tif",
        region_file=r"C:\users\username\output_folder\region.tif",
        output_file=r"C:\users\username\output_folder\RUSLE_KR.tif",
        k_multiplier=1000
    )
    
    
Raster Driver Conversion
-----------------------------

WaTEM/SEDEM does not support raster files in the ``GTiff`` format. Therefore, input rasters must be converted to the Idrisi raster format with the .rst extension,
which is one of the `two raster formats <https://watem-sedem.github.io/watem-sedem/rasterinfo.html#format>`_ supported by WaTEM/SEDEM.

.. code-block:: python
    
    watemsedem.raster_driver_to_rst(
        file_dict={'rusle_p': r"C:\users\username\output_folder\RUSEL_P_buffer.tif"},
        folder_path=r"C:\users\username\output_folder"
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
        stream_file=r"C:\users\username\input_folder\stream.shp",
        stream_col='ws_id',
        dam_list=[21, 22, 5, 31, 17, 24, 27, 2, 13, 1]
    )
    
    # adjacent upstream connectivity
    network.connectivity_adjacent_downstream(
        stream_file=r"C:\users\username\input_folder\stream.shp",
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
        stream_file=r"C:\users\username\input_folder\stream.shp",
        stream_col='ws_id',
        info_file=r"C:\users\username\input_folder\stream_information.txt",
        dam_list=[21, 22, 5, 31, 17, 24, 27, 2, 13, 1]
    )    
    
    # GeoDataFrame of dams' effective upstream drainage polygons
    watemsedem.dam_effective_drainage_area(
        flwdir_file=r"C:\users\username\input_folder\flwdir.shp",
        location_file=r"C:\users\username\input_folder\subbasin_drainage_points.shp",
        location_col='ws_id',
        dam_list=[21, 22, 5, 31, 17, 24, 27, 2, 13, 1],
        folder_path=r"C:\users\username\output_folder"
    )
    
    
Stream Information Files
------------------------------

To support informed decision-making when deploying a dam system within a stream network, it is essential to have comprehensive information for each stream segment.
This includes connectivity, drainage area, and sediment input. The following methods show how to create a TXT file and a shapefile that contain detailed information about stream segments. 
For more information, refer to the documentation of the :meth:`OptiDamTool.Analysis.sediment_delivery_to_stream_txt` and :meth:`OptiDamTool.Analysis.stream_information_shapefile` methods.


.. code-block:: python
    
    # integrate sediment delivery to stream information TXT file
    analysis.sediment_delivery_to_stream_txt(
        input_file=r"C:\users\username\input_folder\stream_information.txt",
        stream_col='ws_id',
        sediment_file=r"C:\users\username\input_folder\Total sediment segments.txt",
        cumsed_file=r"C:\users\username\input_folder\Cumulative sediment segments.txt",
        output_file=r"C:\users\username\output_folder\stream_sediment_delivery.txt"
    )    
    
    # stream shapefile with comprehensive information 
    analysis.stream_information_shapefile(
        stream_file=r"C:\users\username\input_folder\stream.shp",
        info_file=r"C:\users\username\output_folder\stream_sediment_delivery.txt",
        output_file=r"C:\users\username\output_folder\stream_info.shp"
    )
    
    
Effective Upstream Metric Summary of Dams
---------------------------------------------

Once the stream information shapefile is generated using the :meth:`OptiDamTool.Analysis.stream_information_shapefile` method,
it can be used to compute a summary of effective upstream metrics for selected dams. This includes identifying each dam’s directly connected upstream dams,
calculating its effective drainage area, and estimating the corresponding sediment inflow from that area.
These metrics provide a comprehensive understanding of how upstream network structure influences hydrological and sediment contributions to individual dam locations.


.. code-block:: python

    network.effective_upstream_metrics_summary(
        stream_file=r"C:\users\username\output_folder\stream_info.shp",
        stream_col='ws_id',
        dam_list=[21, 22, 5, 31, 17, 24, 27, 2, 13, 1]
    )

 