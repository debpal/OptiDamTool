import GeoAnalyze
import geopandas
import rasterio
import os


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

        Additional shapefiles (not required for WaTEM/SEDEM) are created for detailed analysis:

        - **stream_lines.shp**: Contains a column ``ds_id`` which indicates the adjacent downstream segment. A value of -1 means no downstream connectivity.
        - **subbasins.shp**: Contains a column ``area_m2`` representing the area of each subbasin in square meters.
        - **subbasin_drainage_points.shp**: Contains a column ``flwacc`` representing the flow accumulation at each drainage point.

        The following additional files are also generated:

        - **stream_information.txt**: Contains a table summarizing the shapefiles, with columns ``flw_col``, ``ds_id``, ``area_m2``,
          ``flwacc``, and ``cumarea_m2`` (cumulative drainage area).
        - **summary.json**: Contains a dictionary summarizing the processing time and parameters used.

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
                'flwdir',
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
