import GeoAnalyze
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
        Generates input files required to run the WaTEM/SEDEM model with the extension
        `river routing = 1 <https://watem-sedem.github.io/watem-sedem/model_extensions.html#riverrouting>`_.

            .. note::
                We are assuming the input Digital Elevation Model (DEM) is the exact watershed area,
                hence the function forces all flow directions toward a single outlet at the lowest pit.

        The generated files include:

        - `river segment filename <https://watem-sedem.github.io/watem-sedem/input.html#river-segment-filename>`_: ``stream_lines.tif``
        - `river routing filename <https://watem-sedem.github.io/watem-sedem/input.html#river-routing-filename>`_: ``stream_routing.tif``
        - `adjectant segments <https://watem-sedem.github.io/watem-sedem/input.html#adjectant-segments>`_: ``stream_adjacent_downstream_connectivity.txt``
        - `upstream segments <https://watem-sedem.github.io/watem-sedem/input.html#upstream-segments>`_: ``stream_all_upstream_connectivity.txt``

        Additionally, this function generates shapefiles for:

        - Streams: ``stream_lines.shp``
        - Subbasins: ``subbasins.shp``
        - Subbasin drainage points: ``subbasin_drainage_points.shp``

        All shapefiles include a common identifier column, ``flw_col``, to facilitate cross-referencing.
        While these files are not required to run the WaTEM/SEDEM model, they provide valuable information
        for detailed analysis.

        - `subbasins.shp` contains a column ``area_m2`` representing the area of each subbasin.
        - `subbasin_drainage_points.shp` contains a column ``flwacc`` representing the flow accumulation value at each drainage point.

        A file ``summary.json`` is also generated, detailing processing time and relevant parameters. All output files
        are saved to the specified folder.

        Parameters
        ----------
        dem_file : str
            Path to the input DEM (Digital Elevation Model) file.

        flwacc_percent : float
            A value between 0 and 100 representing the percentage of the maximum flow
            accumulation used to calculate the threshold for stream generation.  The maximum flow
            accumulation corresponds to the total number of valid data cells. To generate streams
            based on a specific threshold cell count, calculate the equivalent percentage relative to
            the total number of valid cells.

        folder_path : str
            Path to the directory where output files will be saved.

        flw_col : str, optional
            Name of the identifier column in shapefiles used for cross-referencing.
            Default is 'ws_id'.

        Returns
        -------
        str
            A message confirming successful creation of the stream-related output files.
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
