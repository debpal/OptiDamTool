import GeoAnalyze
import pyflwdir
import geopandas
import rasterio
import rasterio.features
import os
import typing
import tempfile


class WatemSedem:

    '''
    Provides functionality to prepare the necessary inputs
    for simulating the `WaTEM/SEDEM <https://github.com/watem-sedem>`_ model.
    '''

    def dem_to_stream(
        self,
        dem_file: str,
        flwacc_percent: float,
        folder_path: str,
        flw_col: str = 'ws_id'
    ) -> str:

        '''
        Generates all required input and supporting files for running the WaTEM/SEDEM model
        with the enabled extension `river routing = 1 <https://watem-sedem.github.io/watem-sedem/model_extensions.html#riverrouting>`_.

        This function processes a Digital Elevation Model (DEM) to derive stream networks,
        flow routing, and supporting shapefiles for analysis. It assumes the DEM covers
        a single watershed area and enforces flow convergence toward a single outlet
        at the lowest elevation point. The DEM must use a projected CRS with meter-based units.

        .. note::
            All valid DEM cells are converted to 1 to compute flow accumulation.
            Flow direction is forced toward the lowest pit to simulate a unified outlet.

        The function generates the following files in the specified output directory:

        - **stream_lines.tif**: Raster of river segments.
        - **stream_routing.tif**: Raster of river routing.
        - **stream_adjacent_downstream_connectivity.txt**: Text file of adjacent downstream segments.
        - **stream_all_upstream_connectivity.txt**: Text file of upstream segment connectivity.

        Additional raster and shapefiles (not required for WaTEM/SEDEM) are created for detailed analysis:

        - **flwdir.tif**: Raster of flow direction.
        - **stream_lines.shp**: LineString shapeifle contains a column ``ds_id`` that represents the adjacent downstream segment.
          A value of -1 means no downstream connectivity.
        - **subbasins.shp**: Polygon shapefile contains a column ``area_m2`` that represents the area of each subbasin in square meters.
        - **subbasin_drainage_points.shp**: Point shapefile contains a column ``flwacc`` that represents the flow accumulation at each drainage point.

        The following additional files are also generated:

        - **stream_information.txt**: Contains a table summarizing the shapefiles, with columns ``flw_col``, ``ds_id``, ``area_m2``,
          ``flwacc``, and ``cumarea_m2`` (cumulative drainage area).
        - **summary.json**: Contains a dictionary summarizing the processing time and parameters used.

        .. warning::
            Some files are generated temporarily during the simulation and will be deleted at the end.
            Additionally, any generated files will overwrite existing files if they share the same name.
            It is strongly recommended to use an empty folder as the output directory to prevent accidental deletion
            or overwriting of important files.

        Parameters
        ----------
        dem_file : str
            Path to the input DEM file.

        flwacc_percent : float
            A value between 0 and 100 representing the percentage of the maximum flow
            accumulation used to calculate the threshold for stream generation.  The maximum flow
            accumulation corresponds to the total number of valid data cells. To generate streams
            based on a specific threshold cell count, calculate the equivalent percentage relative to
            the total number of valid cells.

        folder_path : str
            Path to the directory where all output files will be saved.

        flw_col : str, optional
            Name of the identifier column used for cross-referencing in shapefiles.
            Default is 'ws_id'.

        Returns
        -------
        str
            Message confirming successful creation of stream-related output files.
        '''

        # check existence of folder path
        if not os.path.isdir(folder_path):
            raise Exception('Input folder path is not valid.')

        # class objects
        file = GeoAnalyze.File()
        raster = GeoAnalyze.Raster()
        watershed = GeoAnalyze.Watershed()
        stream = GeoAnalyze.Stream()

        # delineation files
        watershed.dem_delineation(
            dem_file=dem_file,
            outlet_type='single',
            tacc_type='percentage',
            tacc_value=flwacc_percent,
            folder_path=folder_path,
            flw_col=flw_col
        )

        # stream raster creation by dem extent
        raster.array_from_geometries(
            shape_file=os.path.join(folder_path, 'stream_lines.shp'),
            value_column=flw_col,
            mask_file=dem_file,
            output_file=os.path.join(folder_path, 'stream_lines.tif'),
            fill_value=0,
            dtype='int16'
        )

        print(
            '\nStream raster creation complete\n',
            flush=True
        )

        # reclassifty flow direction raster accoding to WaTEM/SEDM routing method
        raster.reclassify_by_value_mapping(
            input_file=os.path.join(folder_path, 'flwdir.tif'),
            reclass_map={
                (1, ): 3,
                (2, ): 4,
                (4, ): 5,
                (8, ): 6,
                (16, ): 7,
                (32, ): 8,
                (64, ): 1,
                (128, ): 2
            },
            output_file=os.path.join(folder_path, 'flwdir_reclass.tif')
        )
        # extract reclassified flow direction value by stream raster
        raster.extract_value_by_mask(
            input_file=os.path.join(folder_path, 'flwdir_reclass.tif'),
            mask_file=os.path.join(folder_path, 'stream_lines.tif'),
            output_file=os.path.join(folder_path, 'stream_routing.tif'),
            remove_values=[0],
            fill_value=0
        )

        print(
            'Stream routing raster creation complete\n',
            flush=True
        )

        # adjacent downstream connectivity in the stream network
        stream_gdf = stream._connectivity_adjacent_downstream_segment(
            input_file=os.path.join(folder_path, 'stream_lines.shp'),
            stream_col=flw_col,
            link_col='ds_id',
            unlinked_id=-1
        )
        stream_gdf.to_file(
            filename=os.path.join(folder_path, 'stream_lines.shp')
        )
        dl_df = stream_gdf[[flw_col, 'ds_id']]
        dl_df = dl_df[~dl_df['ds_id'].isin([-1])].reset_index(drop=True)
        dl_df.columns = ['from', 'to']
        dl_df.to_csv(
            path_or_buf=os.path.join(folder_path, 'stream_adjacent_downstream_connectivity.txt'),
            sep='\t',
            index=False
        )

        # all upstream connectivity in the stream network
        ul_df = stream._connectivity_to_all_upstream_segments(
            stream_file=os.path.join(folder_path, 'stream_lines.shp'),
            stream_col=flw_col,
            link_col='us_id',
            unlinked_id=-1
        )
        ul_df = ul_df[~ul_df['us_id'].isin([-1])].reset_index(drop=True)
        ul_df.columns = ['edge', 'upstream edge']
        ul_df['proportion'] = 1.0
        ul_df.to_csv(
            path_or_buf=os.path.join(folder_path, 'stream_all_upstream_connectivity.txt'),
            sep='\t',
            index=False
        )

        # stream information DataFrame
        si_df = stream_gdf[[flw_col, 'ds_id']]
        subbasin_gdf = geopandas.read_file(
            filename=os.path.join(folder_path, 'subbasins.shp')
        )
        si_df = si_df.merge(
            right=subbasin_gdf[[flw_col, 'area_m2']],
            on=flw_col
        )
        pour_gdf = geopandas.read_file(
            filename=os.path.join(folder_path, 'subbasin_drainage_points.shp')
        )
        si_df = si_df.merge(
            right=pour_gdf[[flw_col, 'flwacc']],
            on=flw_col
        )
        with rasterio.open(dem_file) as input_dem:
            dem_res = input_dem.res
        si_df['cumarea_m2'] = si_df['flwacc'] * dem_res[0] * dem_res[1]
        si_df.to_csv(
            path_or_buf=os.path.join(folder_path, 'stream_information.txt'),
            sep='\t',
            index=False
        )

        # delete files that are not required
        file.delete_by_name(
            folder_path=folder_path,
            file_names=[
                'aspect',
                'slope',
                'flwdir_reclass',
                'flwacc',
                'outlet_points',
                'summary'
            ]
        )

        # name change of summary file
        file.name_change(
            folder_path=folder_path,
            rename_map={'summary_swatplus_preliminary_files': 'summary'}
        )

        output = 'All required files has been generated'

        return output

    def extend_model_region(
        self,
        region_file: str,
        buffer_distance: float,
        resolution: float,
        folder_path: str,
        select_values: typing.Optional[list[float]] = None,
        dtype: str = 'int16',
        nodata: float = -9999,
    ) -> rasterio.profiles.Profile:

        '''
        Generates a raster that includes a buffer area around the input region raster file.
        This raster serves as a mask to extend input rasters beyond the model region for use in WaTEM/SEDEM.
        Since WaTEM/SEDEM does not account for NoData values, at least two pixels outside the model domain
        must contain valid data. For more details, `click here <https://watem-sedem.github.io/watem-sedem/input.html#dtm-filename>`_.

        The function generates the following files in the specified output directory:

        - **region.shp**: Polygon shapefile of the model region.
        - **region_buffer.shp**: Polygon shapefile of the model region including the buffer area.
        - **region_buffer_line.shp**: LineString shapefile of the model region including the buffer area.
        - **region_buffe.tif**: Raster file of the model region including the buffer area.

        All shapefiles share a common integer column ``bid``, used for cross-referencing.
        The values in ``bid`` are also used in the output raster file.

        .. warning::
            Generated files will overwrite any existing files with the same names.
            It is strongly recommended to use an empty folder as the output directory
            to prevent accidental overwriting or loss of existing data.

        Parameters
        ----------
        region_file : str
            Path to the input region raster file (e.g., Digital Elevation Model or land cover).

        buffer_distance : float
            Buffer distance (in meters) to apply around the region boundary.

        resolution : float
            Spatial resolution (in meters) of the output raster.

        folder_path : str
            Path to the directory where all output files will be saved.

        select_values : list, optional
            A list of specific values from the ``bid`` column to include.
            If None, all values are used. This is useful for excluding
            small or negligible boundary polygons in **region.shp** after a trial run.

        dtype : str, optional
            Data type of the output raster. Default is 'int16'.

        nodata : float, optional
            NoData value to assign to areas not covered by boundary polygons. Default is -9999.

        Returns
        -------
        profile
            A profile containing metadata about the output raster.
        '''

        # check existence of folder path
        if not os.path.isdir(folder_path):
            raise Exception('Input folder path is not valid.')

        # class objects
        raster = GeoAnalyze.Raster()

        # region boundary GeoDataFrame
        boundary_gdf = raster.boundary_polygon(
            raster_file=region_file,
            shape_file=os.path.join(folder_path, 'region.shp')
        )

        # saving the buffer GeoDataFrame of boundary region
        buffer_gdf = boundary_gdf.copy()
        buffer_gdf.geometry = buffer_gdf.geometry.buffer(buffer_distance)
        buffer_gdf.to_file(
            filename=os.path.join(folder_path, 'region_buffer.shp')
        )

        # buffer line GeoDataFrame of the boundary region
        GeoAnalyze.Shape().polygons_to_boundary_lines(
            input_file=os.path.join(folder_path, 'region_buffer.shp'),
            output_file=os.path.join(folder_path, 'region_buffer_line.shp')
        )

        # saving boundary buffer mask raster array
        output = raster.array_from_geometries_without_mask(
            shape_file=os.path.join(folder_path, 'region_buffer.shp'),
            value_column='bid',
            resolution=resolution,
            output_file=os.path.join(folder_path, 'region_buffer.tif'),
            select_values=select_values,
            dtype=dtype,
            nodata=nodata
        )

        return output

    def extend_raster_nodata_free(
        self,
        input_file: str,
        fill_value: float,
        region_file: str,
        output_file: str
    ) -> rasterio.profiles.Profile:

        '''
        Extends the input raster beyond the model region so that
        the entire output raster contains no NoData values.
        This is useful for preparing input data for WaTEM/SEDEM,
        which does not support NoData cells. For more details,
        see the documentation of :meth:`OptiDamTool.WatemSedem.extend_model_region`.

        Parameters
        ----------
        input_file : str
            Path to the input raster file.

        fill_value : float
            Value to assign to the extended areas and NoData region.

        region_file : str
            Path to the region raster file produced by :meth:`OptiDamTool.WatemSedem.extend_model_region`.

        output_file : str
            Path to save the output raster file.

        Returns
        -------
        profile
            A profile containing metadata about the output raster.
        '''

        # class objects
        raster = GeoAnalyze.Raster()

        with tempfile.TemporaryDirectory() as tmp_dir:
            # raster extension to required region
            raster.extension_to_mask_with_fill_value(
                input_file=input_file,
                mask_file=region_file,
                fill_value=fill_value,
                output_file=os.path.join(tmp_dir, 'temporary.tif')
            )
            # replacing NoData with valid value
            output = raster.nodata_to_valid_value(
                input_file=os.path.join(tmp_dir, 'temporary.tif'),
                valid_value=fill_value,
                output_file=output_file
            )

        return output

    def dam_effective_drainage_polygon(
        self,
        flwdir_file: str,
        location_file: str,
        location_col: str,
        dam_list: list[int],
        folder_path: str
    ) -> geopandas.GeoDataFrame:

        '''
        Generates shapefiles of the selected dam locations and their corresponding effective upstream drainage area polygons,
        saved to the specified output directory. The output shapefiles include a common column, ``location_col``,
        for cross-referencing dam locations.

        - **dam_selected_locations.shp**: Point shapefile of the selected dam locations.
        - **dam_upstream_drainage_area.shp**: Polygon shapefile of the effective upstream drainage areas for the selected dams,
          with an ``area_m2`` column representing the drainage area in square meters.

        Parameters
        ----------
        flwdir_file : str
            Path to the input flow direction raster file ``flowdir.tif``,
            generated by :meth:`OptiDamTool.WatemSedem.dem_to_stream`.

        location_file : str
            Path to the input point shapefile ``subbasin_drainage_points.shp``
            containing all dam locations, generated by :meth:`OptiDamTool.WatemSedem.dem_to_stream`.

        location_col : str
            Name of the column containing unique identifiers for all dam locations.

        dam_list : list
            List of identifiers representing the selected dam locations.

        folder_path : str
            Path to the directory where all output files will be saved.

        Returns
        -------
        GeoDataFrame
            A GeoDataFrame containing polygons of the effective upstream drainage areas for the selected dams,
            with columns ``location_col`` and ``area_m2``.
        '''

        # check existence of folder path
        if not os.path.isdir(folder_path):
            raise Exception('Input folder path is not valid.')

        # flow direction object
        with rasterio.open(flwdir_file) as input_flwdir:
            raster_profile = input_flwdir.profile
            flowdir_object = pyflwdir.from_array(
                data=input_flwdir.read(1),
                transform=input_flwdir.transform
            )

        # all dam location GeoDataFrame
        loc_gdf = geopandas.read_file(location_file)

        # saving selected dam location GeoDataFrame
        dam_gdf = loc_gdf[loc_gdf[location_col].isin(dam_list)].reset_index(drop=True)
        dam_gdf = dam_gdf.drop(
            columns=['flwacc']
        )
        dam_gdf = dam_gdf.sort_values(
            by=[location_col],
            ascending=[True],
            ignore_index=True
        )
        dam_gdf.to_file(
            filename=os.path.join(folder_path, 'dam_selected_locations.shp')
        )

        # upstream drainage area
        drainage_array = flowdir_object.basins(
            xy=(dam_gdf.geometry.x, dam_gdf.geometry.y),
            ids=dam_gdf[location_col].astype('uint32')
        )
        drainage_shapes = rasterio.features.shapes(
            source=drainage_array.astype('int32'),
            mask=drainage_array != 0,
            transform=raster_profile['transform'],
            connectivity=8
        )
        drainage_features = [
            {'geometry': geometry, 'properties': {location_col: value}} for geometry, value in drainage_shapes
        ]
        drainage_gdf = geopandas.GeoDataFrame.from_features(
            features=drainage_features,
            crs=raster_profile['crs']
        )
        drainage_gdf = drainage_gdf.sort_values(
            by=[location_col],
            ascending=[True],
            ignore_index=True
        )
        drainage_gdf['area_m2'] = drainage_gdf.geometry.area.round(decimals=1)

        # saving upstream drainage area GeoDataFrame
        polygon_schema = {
            'geometry': 'Polygon',
            'properties': {
                location_col: 'int',
                'area_m2': 'float:19.1'
            }
        }
        drainage_gdf.to_file(
            filename=os.path.join(folder_path, 'dam_upstream_drainage_area.shp'),
            schema=polygon_schema,
            engine='fiona'
        )

        return drainage_gdf
