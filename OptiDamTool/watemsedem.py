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

    def __init__(
        self
    ) -> None:

        self.file = GeoAnalyze.File()
        self.raster = GeoAnalyze.Raster()
        self.shape = GeoAnalyze.Shape()
        self.watershed = GeoAnalyze.Watershed()
        self.stream = GeoAnalyze.Stream()

    @property
    def land_cover_mapping(
        self
    ) -> dict[tuple[int, ...], int]:

        '''
        Dictionary mapping between `Esri values <https://www.arcgis.com/home/item.html?id=cfcb7609de5f478eb7666240902d4d3d>`_
        and `WaTEM/SEDEM values <https://watem-sedem.github.io/watem-sedem/input.html#parcel-filename>`_ of land cover classes.

        .. warning::

            The default reclassification will be used in :meth:`OptiDamTool.WatemSedem.land_cover_esri`
            if no custom input is provided and the raster contains Esri land cover classes.
            This mapping is specifically tailored for arid regions in the Kingdom of Saudi Arabia.
            If this mapping is not appropriate for the user's model region,
            a custom reclassification dictionary must be supplied.

            ===================  ===========  ==================  =================
            Esri Name            Esri Value   WaTEM/SEDEM Value   WaTEM/SEDEM Name
            ===================  ===========  ==================  =================
            Water                1            -5                  Open water
            Trees                2            -3                  Forest
            Flooded vegetation   4            -4                  Pasture
            Crops                5            ¹> 0                Agricultural fields
            Built area           7            -2                  Infrastructure
            Bare ground          8            -4                  Pasture
            Snow/ice             9            -5                  Open water
            Rangeland            11           -4                  Pasture
            ===================  ===========  ==================  =================

            ¹Internal processing is handled within the function. "NA" stands for Not Applicable.
        '''

        lc_map = {
            (1, 9): -5,
            (2, ): -3,
            (7, ): -2,
            (4, 8, 11): -4

        }

        return lc_map

    @property
    def land_management_mapping(
        self
    ) -> dict[tuple[int, ...], float]:

        '''
        Dictionary mapping between land cover classes and their corresponding land management factor values.

        .. warning::

            The default reclassification will be used in :meth:`OptiDamTool.WatemSedem.land_management_factor`
            if no custom input is provided and the raster contains Esri land cover classes.
            These reclassification values are taken from a global analysis of land management factors by
            `Xiong et al. (2023) <https://doi.org/10.3390/rs15112868>`_. This mapping is specifically tailored
            for arid regions in the Kingdom of Saudi Arabia. If this mapping is not appropriate for the user's model region,
            a custom reclassification dictionary must be supplied.

            ===================  ===========  ==================
            Esri Name            Esri Value   Management value
            ===================  ===========  ==================
            Water                1            0
            Trees                2            0.013
            Flooded vegetation   4            0.105
            Crops                5            0.301
            Built area           7            0.22
            Bare ground          8            1
            Rangeland            11           0.374
            ===================  ===========  ==================
        '''

        lm_map = {
            (1, ): 0,
            (2, ): 0.013,
            (4, ): 0.105,
            (5, ): 0.301,
            (7, ): 0.22,
            (-1, 8): 1,
            (11, ): 0.374
        }

        return lm_map

    def _write_stream_shapefile(
        self,
        stream_gdf: geopandas.GeoDataFrame,
        stream_file: str
    ) -> None:

        '''
        Writes a stream GeoDataFrame containing columns with large values to a shapefile,
        mitigating ``RuntimeWarning`` when exporting to the DBF file.

        Parameters
        ----------
        gdf : GeoDataFrame
            Input GeoDataFrame.

        output_file : str
            Path to the output file.

        Returns
        -------
        None
        '''

        target_cols = [
            'isa_m2',
            'flwacc',
            'csa_m2',
            'sed_kg',
            'cumsed_kg',
            'sed_ton',
            'cumsed_ton'
        ]

        property_cols = [col for col in stream_gdf.columns if col != 'geometry']
        property_dict = {
            col: 'int' if col not in target_cols else 'float:19.2' for col in property_cols
        }
        stream_gdf.to_file(
            filename=stream_file,
            schema={
                'geometry': 'LineString',
                'properties': property_dict
            },
            engine='fiona'
        )

        return None

    def dem_to_stream(
        self,
        dem_file: str,
        flwacc_percent: float,
        folder_path: str
    ) -> geopandas.GeoDataFrame:

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

        Additional raster and shapefiles (not required for WaTEM/SEDEM) are generated for detailed analysis.
        The shapefiles include a common column, ``ws_id``, which cross-references each stream segment identifier
        with its drainage point and subbasin area.

        - **flwdir.tif**: Raster of flow direction.
        - **stream_lines.shp**: LineString shapefile with columns:
            - ``ds_id``: Identifies of the adjacent downstream segment (-1 if no downstream connectivity).
            - ``isa_m2``: Individual subbasin area of the segment (renamed ``area_m2`` from ``subbasins.shp``), in sqaure meters.
            - ``flwacc``: Flow accumulation value fetched from ``subbasin_drainage_points.shp``.
            - ``csa_m2``: Cumulative subbasin area from upstream heads, in square meters.
        - **subbasins.shp**: Polygon shapefile contains a column ``area_m2`` that represents the area of each subbasin in square meters.
        - **subbasin_drainage_points.shp**: Point shapefile contains a column ``flwacc`` that represents the flow accumulation at each drainage point.
          The flow accumulation values are calculated from a raster in which all valid DEM cells are converted to 1.

        The following additional files are also generated:

        - **stream_information.json**: Table of all attributes from ``stream_lines.shp`` (excluding geometry),
          allowing stream analysis without directly opening the shapefile.
        - **summary.json**: Dictionary summarizing processing time and parameters used.

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

        Returns
        -------
        GeoDataFrame
            A GeoDataFrame containing information about the stream network.
        '''

        # check existence of folder path
        if not os.path.isdir(folder_path):
            raise NotADirectoryError('Input folder_path is not valid')

        # delineation files
        flw_col = 'ws_id'
        self.watershed.dem_delineation(
            dem_file=dem_file,
            outlet_type='single',
            tacc_type='percentage',
            tacc_value=flwacc_percent,
            folder_path=folder_path,
            flw_col=flw_col
        )

        # stream raster creation by dem extent
        self.raster.array_from_geometries(
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
        self.raster.reclassify_by_value_mapping(
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
        self.raster.extract_value_by_mask(
            input_file=os.path.join(folder_path, 'flwdir_reclass.tif'),
            mask_file=os.path.join(folder_path, 'stream_lines.tif'),
            output_file=os.path.join(folder_path, 'stream_routing.tif'),
            remove_values=[0],
            fill_value=0,
            dtype='int16'
        )

        print(
            'Stream routing raster creation complete\n',
            flush=True
        )

        # adjacent downstream connectivity in the stream network
        stream_gdf = self.stream._connectivity_adjacent_downstream_segment(
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
        ul_df = self.stream._connectivity_to_all_upstream_segments(
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
        si_df = si_df.rename(
            columns={
                'area_m2': 'isa_m2'
            }
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
        si_df['csa_m2'] = si_df['flwacc'] * dem_res[0] * dem_res[1]
        si_df.to_json(
            path_or_buf=os.path.join(folder_path, 'stream_information.json'),
            orient='records',
            lines=True
        )

        # merging stream GeoDataFrame with information DataFrame
        common_cols = [col for col in si_df.columns if col in stream_gdf.columns]
        stream_gdf = stream_gdf.merge(
            right=si_df,
            on=common_cols
        )
        self._write_stream_shapefile(
            stream_gdf=stream_gdf,
            stream_file=os.path.join(folder_path, 'stream_lines.shp')
        )

        # delete files that are not required
        self.file.delete_by_name(
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
        self.file.name_change(
            folder_path=folder_path,
            rename_map={'summary_swatplus_preliminary_files': 'summary'}
        )

        return stream_gdf

    def model_region_extension(
        self,
        dem_file: str,
        buffer_units: int,
        folder_path: str,
        select_values: typing.Optional[list[float]] = None,
        dtype: str = 'int16',
        nodata: float = -9999,
    ) -> dict[str, float]:

        '''
        Generates a raster with a buffer area around the input Digital Elevation Model (DEM) raster.
        This raster serves as a mask to extend input rasters beyond the model region.
        Since WaTEM/SEDEM does not handle NoData values properly, at least two DEM pixels
        outside the model domain must contain valid data. For details, refer to the
        `input DEM requirements <https://watem-sedem.github.io/watem-sedem/input.html#dtm-filename>`_.

        The function generates the following files in the specified output directory:

        - **region.tif**: Constant raster with value 1 over the DEM region.
        - **region.shp**: Polygon shapefile of the DEM region.
        - **region_buffer.tif**: Raster file of the extended DEM region including the buffer area.
        - **region_buffer.shp**: Polygon shapefile of the extended DEM region including the buffer area.

        All shapefiles contain a common column ``rst_val``, used for cross-referencing.
        This column contains the corresponding values from the output raster files.

        .. tip::
            After generating ``region_buffer.shp``, use this shapefile to clip the DEM,
            including the buffer area, from the extended DEM raster.

        .. warning::
            Generated files will overwrite any existing files with the same names.
            It is strongly recommended to use an empty folder as the output directory
            to prevent accidental overwriting or loss of existing data.

        Parameters
        ----------
        dem_file : str
            Path to the input DEM raster file.

        buffer_units : int
            Buffer size, expressed in units of the DEM resolution.
            For example, if the DEM resolution is 10 meters and ``buffer_units`` is 50,
            the function applies a 500-meter buffer (10 × 50) around the DEM boundary.

        folder_path : str
            Path to the directory where all output files will be saved.

        select_values : list, optional
            A list of specific values from the ``rst_val`` column to include.
            If None, all values are used. This is useful for excluding
            small or negligible boundary polygons in **region.shp** after a trial run.

        dtype : str, optional
            Data type of the output raster. Default is 'int16'.

        nodata : float, optional
            NoData value to assign to areas not covered by boundary polygons. Default is -9999.

        Returns
        -------
        dict
            A dictionary containing information of actual and extended areas, including their difference.
        '''

        # check existence of folder path
        if not os.path.isdir(folder_path):
            raise NotADirectoryError('Input folder_path is not valid')

        # region constant raster
        self.raster.reclassify_by_constant_value(
            input_file=dem_file,
            constant_value=1,
            output_file=os.path.join(folder_path, 'region.tif'),
            dtype=dtype
        )

        # region buffer boundary GeoDataFrame
        boundary_gdf = self.raster.array_to_geometries(
            raster_file=os.path.join(folder_path, 'region.tif'),
            shape_file=os.path.join(folder_path, 'region.shp')
        )

        # DEM resolution
        with rasterio.open(dem_file) as input_dem:
            dem_resolution = input_dem.res[0]

        # saving the buffer GeoDataFrame of boundary region
        buffer_gdf = boundary_gdf.copy()
        buffer_gdf.geometry = buffer_gdf.geometry.buffer(
            distance=dem_resolution * buffer_units
        )
        buffer_gdf.to_file(
            filename=os.path.join(folder_path, 'region_buffer.shp')
        )

        # saving boundary buffer mask raster array
        self.raster.array_from_geometries_without_mask(
            shape_file=os.path.join(folder_path, 'region_buffer.shp'),
            value_column='rst_val',
            resolution=dem_resolution,
            output_file=os.path.join(folder_path, 'region_buffer.tif'),
            select_values=select_values,
            dtype=dtype,
            nodata=nodata
        )

        # region buffer boundary GeoDataFrame
        buffer_gdf = self.raster.array_to_geometries(
            raster_file=os.path.join(folder_path, 'region_buffer.tif'),
            shape_file=os.path.join(folder_path, 'region_buffer.shp')
        )

        output = {
            'actual area (m^2)': round(sum(boundary_gdf.area)),
            'extended area (m^2)': round(sum(buffer_gdf.area)),
            'difference area (m^2)': round(sum(buffer_gdf.area) - sum(boundary_gdf.area))
        }

        return output

    def raster_clipping_by_bounding_box(
        self,
        input_file: str,
        shape_file: str,
        output_file: str,
        buffer_length: float = 0,
        nodata: float = -9999,
        dtype: typing.Optional[str] = None
    ) -> rasterio.profiles.Profile:

        '''
        Clips a raster using a rectangular bounding box derived from the total bounds
        of an input shapefile. If necessary, the Coordinate Reference System (CRS)
        of the shapefile is automatically transformed to match the raster’s CRS.
        This function is useful for extracting specific regions from large rasters for focused analysis.

        Parameters
        ----------
        input_file : str
            Path to the input raster file.

        shape_file : str
            Path to the input shapefile whose total bounds will be used to clip the raster.

        output_file : str
            Path to the output raster file.

        dtype : str, optional
            Data type of the output raster. Default is 'int16'.

        nodata : float, optional
            NoData value of the output raster. Default is -9999.

        dtype : str, optional
            Data type of the output raster.
            If None, the data type of the input raster is retained.

        Returns
        -------
        profile
            A profile containing metadata about the output raster.
        '''

        # boundary box of the shapefile
        with tempfile.TemporaryDirectory() as tmp_dir:
            self.shape.boundary_box(
                input_file=shape_file,
                output_file=os.path.join(tmp_dir, 'box.shp'),
                buffer_length=buffer_length
            )
            # saving clipped raster
            self.raster.clipping_by_shapes(
                input_file=input_file,
                shape_file=os.path.join(tmp_dir, 'box.shp'),
                output_file=os.path.join(tmp_dir, 'temporary.tif')
            )
            output_profile = self.raster.nodata_value_change(
                input_file=os.path.join(tmp_dir, 'temporary.tif'),
                nodata=nodata,
                output_file=output_file,
                dtype=dtype
            )

        return output_profile

    def raster_reproject_clipping_rescaling(
        self,
        input_file: str,
        resampling_method: str,
        shape_file: str,
        mask_file: str,
        output_file: str,
        nodata: typing.Optional[float] = None
    ) -> rasterio.profiles.Profile:

        '''
        Reprojects a raster using the Coordinate Reference System (CRS) of the input shapefile,
        then clips the reprojected raster based on that shapefile. The provided mask raster, which shares
        the same extent as the shapefile, is used to rescale the resolution of the reprojected and clipped raster.
        This function is useful for performing focused analysis on rasters obtained via
        :meth:`OptiDamTool.WatemSedem.raster_clipping_by_bounding_box`.

        Parameters
        ----------
        input_file : str
            Path to the input raster file.

        resampling_method : str
            Resampling method to apply during reprojection. The
            supported options are 'nearest', 'bilinear', and 'cubic'.

        shape_file : str
            Path to the shapefile named ``region.shp``, generated by
            :meth:`OptiDamTool.WatemSedem.model_region_extension`, used to clip the raster.

        mask_file : str
            Path to the region raster named ``region.tif``, produced by
            :meth:`OptiDamTool.WatemSedem.model_region_extension`, used to rescale
            the resolution of the output raster.

        output_file : str
            Path to save the output raster file.

        nodata : float, optional
            The NoData value to assign in the output raster.
            If None, the NoData value from the input raster is retained.

        Returns
        -------
        profile
            A profile containing metadata about the output raster.
        '''

        # input GeoDataFrame
        gdf = geopandas.read_file(shape_file)

        # temporary directory
        with tempfile.TemporaryDirectory() as tmp_dir:
            # raster reprojection
            self.raster.crs_reprojection(
                input_file=input_file,
                resampling_method=resampling_method,
                target_crs=str(gdf.crs),
                output_file=os.path.join(tmp_dir, 'tmp_1.tif'),
                nodata=nodata
            )
            # raster clipping
            self.raster.clipping_by_shapes(
                input_file=os.path.join(tmp_dir, 'tmp_1.tif'),
                shape_file=shape_file,
                output_file=os.path.join(tmp_dir, 'tmp_2.tif')
            )
            # raster resolution rescaling
            output = self.raster.resolution_rescaling_with_mask(
                input_file=os.path.join(tmp_dir, 'tmp_2.tif'),
                mask_file=mask_file,
                resampling_method=resampling_method,
                output_file=output_file
            )

        return output

    def raster_extension(
        self,
        input_file: str,
        region_file: str,
        output_file: str,
        fill_value: float = 0,
        dtype: typing.Optional[str] = None,
        nodata: typing.Optional[float] = None
    ) -> rasterio.profiles.Profile:

        '''
        Extends the input raster to match the region file and replaces NoData values with a valid value.
        This is useful for preparing input data for WaTEM/SEDEM, which does not support NoData cells.
        For details, refer to the `input requirements <https://watem-sedem.github.io/watem-sedem/input.html#dtm-filename>`_.

        Parameters
        ----------
        input_file : str
            Path to the input raster file.

        region_file : str
            Path to the region raster including buffer area, ``region_buffer.tif``,
            produced by :meth:`OptiDamTool.WatemSedem.model_region_extension`.

        output_file : str
            Path to save the output raster file.

        fill_value : float
            Value to assign to the extended areas and NoData region. Default is 0.

        dtype : str, optional
            Data type of the output raster.
            If None, the data type of the input raster is retained.

        nodata : float, optional
            NoData value to assign in the output raster.
            If None, the NoData value of the input raster is retained.

        Returns
        -------
        profile
            A profile containing metadata about the output raster.
        '''

        with tempfile.TemporaryDirectory() as tmp_dir:
            # extending raster and fill buffer area value
            self.raster.reclassify_value_outside_boundary(
                area_file=input_file,
                extent_file=region_file,
                outside_value=fill_value,
                output_file=os.path.join(tmp_dir, 'temporary.tif'),
                dtype=dtype,
                nodata=nodata
            )
            # replacing NoData with valid value
            output = self.raster.nodata_to_valid_value(
                input_file=os.path.join(tmp_dir, 'temporary.tif'),
                valid_value=fill_value,
                output_file=output_file
            )

        return output

    def raster_constant_extension(
        self,
        input_file: str,
        constant_value: float,
        region_file: str,
        output_file: str,
        fill_value: float = 0,
        dtype: typing.Optional[str] = None,
        nodata: typing.Optional[float] = None
    ) -> rasterio.profiles.Profile:

        '''
        Creates a constant raster by assigning a specified value to all valid pixels.
        The raster is further extended to exdented region file and NoData is replaced by a valid value.
        This is useful for preparing a constant raster, for example the
        `erosion control factor <https://watem-sedem.github.io/watem-sedem/watem-sedem.html#p-factor>`_,
        in an efficient way, often required for small regions when running WaTEM/SEDEM.

        .. note::
            If raster extension is not required, the same ``region.tif``
            file must be used for both the input and region rasters.

        Parameters
        ----------
        input_file : str
            Path to the region raster named ``region.tif``, produced by
            :meth:`OptiDamTool.WatemSedem.model_region_extension`.

        constant_value : float
            The constant value to assign to all valid pixels in the output raster.

        region_file : str
            Path to the extended region raster named ``region_buffer.tif``,
            produced by :meth:`OptiDamTool.WatemSedem.model_region_extension`.

        output_file : str
            Path to save the output raster file.

        fill_value : float
            Value to assign to the extended areas and NoData region. Default is 0.

        dtype : str, optional
            Data type of the output raster.
            If None, the data type of the region raster is retained.

        nodata : float, optional
            NoData value to assign in the output raster.
            If None, the NoData value of the region raster is retained.

        Returns
        -------
        profile
            A profile containing metadata about the output raster.
        '''

        # temporary directory
        with tempfile.TemporaryDirectory() as tmp_dir:
            # constant raster
            self.raster.reclassify_by_constant_value(
                input_file=input_file,
                constant_value=constant_value,
                output_file=os.path.join(tmp_dir, 'temporary.tif'),
                dtype=dtype
            )
            # extending constant raster
            output = self.raster_extension(
                input_file=os.path.join(tmp_dir, 'temporary.tif'),
                region_file=region_file,
                output_file=output_file,
                fill_value=fill_value,
                dtype=dtype,
                nodata=nodata
            )

        return output

    def rusle_kr(
        self,
        k_file: str,
        r_file: str,
        region_file: str,
        output_file: str,
        k_multiplier: float = 1,
    ) -> rasterio.profiles.Profile:

        '''
        Generates a raster map by multiplying the soil erodibility (K) and rainfall erosivity (R) factor rasters.
        While WaTEM/SEDEM typically uses a raster for K and a single value for R in small regions,
        this function multiplies the K and R rasters when both vary spatially across a larger area.
        For more details, see the `R-factor documentation <https://watem-sedem.github.io/watem-sedem/watem-sedem.html#r-factor>`_.

        .. warning::
            WaTEM/SEDEM uses the units of R and K as [MJ·mm]/[ha·h·year] and [kg·h]/[MJ·mm], respectively.
            If the K raster values are in tons, they must be converted to kilograms using the `k_multiplier`.
            There is no need to convert hectares to square meters in the R values. All input rasters (K, R, and region)
            must have the same Coordinate Reference System (CRS), resolution, and cell alignment.
            For details, refer to the `formulas and units <https://watem-sedem.github.io/watem-sedem/formulas-units.html#overview-of-formulas-and-units-in-watem-sedem>`_.

        Parameters
        ----------
        k_file : str
            Path to the input raster file representing the soil erodibility factor (K).

        r_file : str
            Path to the input raster file representing the rainfall erosivity factor (R).

        region_file : str
            Path to the region raster named ``region.tif``, produced by
            :meth:`OptiDamTool.WatemSedem.model_region_extension`. Used for internal alignment and masking.

        output_file : str
            Path to save the output raster file.

        k_multiplier : float, optional
            Multiplier used to convert K values, e.g., from tons to kilograms.
            Default is 1, meaning no conversion is applied.

        Returns
        -------
        profile
            A profile containing metadata about the output raster.
        '''

        # read the region array
        with rasterio.open(region_file) as input_region:
            region_profile = input_region.profile
            nodata_array = input_region.read(1) == region_profile['nodata']
        # k-factor raster array and unit conversion
        with rasterio.open(k_file) as input_k:
            k_array = k_multiplier * input_k.read(1)
        # read the R-factor raster array
        with rasterio.open(r_file) as input_r:
            r_array = input_r.read(1)
        # multiplication of K and R facotrs
        kr_array = k_array * r_array
        kr_array[nodata_array] = region_profile['nodata']
        # saving K-factor array
        kr_array = kr_array.round().astype('int16')
        region_profile['dtype'] = 'int16'
        with rasterio.open(output_file, 'w', **region_profile) as output_kr:
            output_kr.write(kr_array, 1)
            output = output_kr.profile

        return output

    def land_cover_esri(
        self,
        lc_file: str,
        stream_file: str,
        folder_path: str,
        reclass_dict: typing.Optional[dict[tuple[int, ...], int]] = None
    ) -> str:

        '''
        Processes a high-resolution, open-source `Esri land cover <https://livingatlas.arcgis.com/landcover/>`_ raster
        of the model region for WaTEM/SEDEM simulation.

        - **land_cover_percent_esri.csv**: Contains the input
          `Esri land cover raster <https://www.arcgis.com/home/item.html?id=cfcb7609de5f478eb7666240902d4d3d>`_ values,
          along with cell counts, percentage counts, cumulative percentages, and class names.

        - **land_cover_cropland_unsplit.tif**: Reclassified Esri land cover raster using
          `WaTEM/SEDEM land cover class values <https://watem-sedem.github.io/watem-sedem/input.html#parcel-filename>`_,
          with stream lines overlaid (using raster value -1). If the cropland class with Esri value 5 is present,
          it is not reclassified here due to its need in further processing.

        - **land_cover_percent_watemsedem.csv**: Contains the WaTEM/SEDEM land cover raster values,
          including counts, count percentages, cumulative percentages, and class names.

        - **land_cover_extract_cropland.shp**: Polygon shapefile of crop fields extracted from ``land_cover_cropland_unsplit.tif``,
          with a ``c_id`` column representing polygon identifiers.

        - **land_cover_cropland_split.tif**: Raster created by overlaying crop fields onto ``land_cover_cropland_unsplit.tif``.

        The last two files, ``land_cover_extract_cropland.shp`` and ``land_cover_cropland_split.tif``,
        are generated **only if** the cropland class (Esri value 5) is present in the input land cover raster.

        Parameters
        ----------
        lc_file : str
            Path to the input land cover raster file of the model region, produced by
            :meth:`OptiDamTool.WatemSedem.raster_reproject_clipping_rescaling`. See the
            `user guide <https://github.com/debpal/OptiDamTool/blob/main/userguide_OptiDamTool.ipynb>`_ for more details.

        stream_file : str
            Path to the stream shapefile, produced by :meth:`OptiDamTool.WatemSedem.dem_to_stream`.

        folder_path : str
            Path to the directory where all output files will be saved.

        reclass_map : dict, optional
            Reclassification dictionary between Esri and WaTEM/SEDEM land cover class values.
            Each key is a tuple of Esri land cover values, and the corresponding value is
            an integer representing the WaTEM/SEDEM class. If not provided, the default mapping
            defined in :attr:`OptiDamTool.WatemSedem.land_cover_mapping` is used.

        Returns
        -------
        str
            A message containing the number of agricultural fields detected in the output raster.
        '''

        # check existence of folder path
        if not os.path.isdir(folder_path):
            raise NotADirectoryError('Input folder_path is not valid')

        # temporary directory
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Esri land cover classes percentage
            esri_df = self.raster.count_unique_values(
                raster_file=lc_file,
                csv_file=os.path.join(tmp_dir, 'lc_percent_esri.csv')
            )
            lc_esri = {
                1: 'Water',
                2: 'Trees',
                4: 'Flooded vegetation',
                5: 'Crops',
                7: 'Built area',
                8: 'Bare ground',
                9: 'Snow/ice',
                10: 'Clouds',
                11: 'Rangeland',
            }
            esri_df['Class'] = esri_df['Value'].apply(lambda x: lc_esri.get(x))
            esri_df.to_csv(
                path_or_buf=os.path.join(folder_path, 'land_cover_percent_esri.csv'),
                sep='\t',
                index=False,
                float_format='%.3f'
            )
            # adding -1 as general identifier for stream lines
            stream_gdf = geopandas.read_file(stream_file)
            stream_gdf['sg_id'] = - 1
            self._write_stream_shapefile(
                stream_gdf=stream_gdf,
                stream_file=os.path.join(tmp_dir, 'stream.shp')
            )
            # paste stream geometries to land cover raster
            self.raster.overlaid_with_geometries(
                input_file=lc_file,
                shape_file=os.path.join(tmp_dir, 'stream.shp'),
                value_column='sg_id',
                output_file=os.path.join(tmp_dir, 'adding_stream.tif')
            )
            # reclassification of land cover map
            reclass_map = self.land_cover_mapping if reclass_dict is None else reclass_dict
            self.raster.reclassify_by_value_mapping(
                input_file=os.path.join(tmp_dir, 'adding_stream.tif'),
                reclass_map=reclass_map,
                output_file=os.path.join(folder_path, 'land_cover_cropland_unsplit.tif')
            )
            # WaTEM/SEDEM land cover classes percentage
            ws_df = self.raster.count_unique_values(
                raster_file=os.path.join(folder_path, 'land_cover_cropland_unsplit.tif'),
                csv_file=os.path.join(tmp_dir, 'lc_percent_watemsedem.csv'),
                ascending_values=False
            )
            lc_ws = {
                5: 'Agricultural fields',
                -1: 'River',
                -2: 'Infrastructure',
                -3: 'Forest',
                -4: 'Pasture',
                -5: 'Open water',
                -6: 'Grass strips'
            }
            ws_df['Class'] = ws_df['Value'].apply(lambda x: lc_ws.get(x))
            ws_df.to_csv(
                path_or_buf=os.path.join(folder_path, 'land_cover_percent_watemsedem.csv'),
                sep='\t',
                index=False,
                float_format='%.3f'
            )
            agri_field = 0
            # if agriculture class exist in the land cover
            if 5 in ws_df['Value'].tolist():
                # extract agriculture field polygons
                self.raster.array_to_geometries(
                    raster_file=os.path.join(folder_path, 'land_cover_cropland_unsplit.tif'),
                    select_values=[5],
                    shape_file=os.path.join(tmp_dir, 'crop.shp')
                )
                # adding identifiers to the agricultural field polygons
                self.shape.column_add_for_id(
                    input_file=os.path.join(tmp_dir, 'crop.shp'),
                    column_name='c_id',
                    output_file=os.path.join(folder_path, 'land_cover_extract_cropland.shp')
                )
                # paste agriculture field polygons to land cover raster
                raster_values = self.raster.overlaid_with_geometries(
                    input_file=os.path.join(folder_path, 'land_cover_cropland_unsplit.tif'),
                    shape_file=os.path.join(folder_path, 'land_cover_extract_cropland.shp'),
                    value_column='c_id',
                    output_file=os.path.join(folder_path, 'land_cover_cropland_split.tif'),
                    all_touched=False
                )
                agri_field = max(raster_values)

        output = f'Total agricultural lands identified: {agri_field}'

        return output

    def land_management_factor(
        self,
        lc_file: str,
        stream_file: str,
        output_file: str,
        reclass_dict: typing.Optional[dict[tuple[int, ...], int]] = None
    ) -> list[float]:

        '''
        Generates a land management `C-factor <https://watem-sedem.github.io/watem-sedem/watem-sedem.html#c-factor>`_ raster
        for the model region, suitable for WaTEM/SEDEM simulation.

        .. tip::
            The input stream shapefile will be overlaid onto the land cover raster using the value -1,
            as WaTEM/SEDEM designates this as the river class. If any non-river class already uses the value -1
            in the input land cover raster, it is recommended to assign a different value to avoid conflicts.

        Parameters
        ----------
        lc_file : str
            Path to the input land cover raster file of the model region.

        stream_file : str
            Path to the stream shapefile, produced by :meth:`OptiDamTool.WatemSedem.dem_to_stream`.

        output_file : str
            Path to save the output raster file.

        reclass_map : dict, optional
            Reclassification dictionary where each key is a tuple of land cover class values,
            and each corresponding value is a land management factor (between 0 and 1).
            If not provided, the default mapping from :attr:`OptiDamTool.WatemSedem.land_management_mapping`
            will be used, assuming the input raster contains Esri land cover classes.

        Returns
        -------
        list
            A list of land management factor values from the output raster,
            confirming successful reclassification.
        '''

        # temporary directory
        with tempfile.TemporaryDirectory() as tmp_dir:
            # adding -1 as general identifier for stream lines
            stream_gdf = geopandas.read_file(stream_file)
            stream_gdf['gs_id'] = -1
            self._write_stream_shapefile(
                stream_gdf=stream_gdf,
                stream_file=os.path.join(tmp_dir, 'stream.shp')
            )
            # paste stream geometries to land cover raster
            self.raster.overlaid_with_geometries(
                input_file=lc_file,
                shape_file=os.path.join(tmp_dir, 'stream.shp'),
                value_column='gs_id',
                output_file=os.path.join(tmp_dir, 'landuse_stream.tif')
            )
            # land management factor
            reclass_map = self.land_management_mapping if reclass_dict is None else reclass_dict
            output = self.raster.reclassify_by_value_mapping(
                input_file=os.path.join(tmp_dir, 'landuse_stream.tif'),
                reclass_map=reclass_map,
                output_file=output_file,
                dtype='float32'
            )

        return list(output)

    def raster_driver_to_rst(
        self,
        file_dict: dict[str, str],
        folder_path: str
    ) -> list[str]:

        '''
        Converts raster files to the Idrisi raster format (RST), which is one of the two
        `raster formats <https://watem-sedem.github.io/watem-sedem/rasterinfo.html#format>`_
        supported by WaTEM/SEDEM.

        Parameters
        ----------
        file_dict : dict
            A dictionary where each key is the desired output file name (without path or extension),
            and the corresponding value is the full path to the input raster file in a non-Idrisi format.

        folder_path : str
            Path to the directory where all converted output files will be saved.
            For example, if 'dem' is a key in input file dictionary, the resulting file will be saved as 'dem.rst' in this folder.

        Returns
        -------
        list
            A list of successfully generated files with the ``.rst`` extension in the output directory.
        '''

        # raster conversion and save it to the dictionary
        output_dict = {}
        for file in file_dict:
            input_file = file_dict[file]
            output_file = os.path.join(folder_path, file + '.rst')
            GeoAnalyze.Raster().driver_convert(
                input_file=input_file,
                target_driver='RST',
                output_file=output_file
            )
            output_dict[file + '.rst'] = output_file

        output = [
            file for file in output_dict if os.path.exists(output_dict[file])
        ]

        return output

    def dam_controlled_drainage_polygons(
        self,
        flwdir_file: str,
        location_file: str,
        dam_list: list[int],
        folder_path: str
    ) -> dict[str, geopandas.GeoDataFrame]:

        '''
        Generates GeoJSON files of the selected dam locations and their corresponding effective upstream drainage area polygons,
        saved to the specified output directory. The output GeoJSON files include a common column, ``ws_id``,
        for cross-referencing dam locations.

        - **dam_location_point.geojson**: Point shapefile of the selected dam locations.
        - **dam_drainage_polygon.geojson**: Polygon shapefile of the effective upstream drainage areas for the selected dams,
          with an ``area_m2`` column representing the drainage area in square meters.

        Parameters
        ----------
        flwdir_file : str
            Path to the input flow direction raster file ``flowdir.tif``,
            generated by :meth:`OptiDamTool.WatemSedem.dem_to_stream`.

        location_file : str
            Path to the input point shapefile ``subbasin_drainage_points.shp``
            containing all dam locations, generated by :meth:`OptiDamTool.WatemSedem.dem_to_stream`.

        dam_list : list
            List of identifiers representing the selected dam locations.

        folder_path : str
            Path to the directory where all output files will be saved.

        Returns
        -------
        dict
            A dictionary with two keys: ``dam_location_point``, a Point GeoDataFrame of dam locations,
            and ``dam_drainage_polygon``, a Polygon GeoDataFrame of the corresponding drainage areas.
            Both GeoDataFrames include the ``ws_id`` for cross-referencing.
            The drainage area GeoDataFrame also includes an ``area_m2`` column
            representing the drainage area in square meters.
        '''

        # check existence of folder path
        if not os.path.isdir(folder_path):
            raise NotADirectoryError('Input folder_path is not valid')

        # flow direction object
        with rasterio.open(flwdir_file) as input_flwdir:
            raster_profile = input_flwdir.profile
            flowdir_object = pyflwdir.from_array(
                data=input_flwdir.read(1),
                transform=input_flwdir.transform
            )

        # all dam location GeoDataFrame
        loc_col = 'ws_id'
        loc_gdf = geopandas.read_file(location_file)
        loc_gdf = loc_gdf[[loc_col, 'geometry']]

        # selected dam location GeoDataFrame
        dam_gdf = loc_gdf[loc_gdf[loc_col].isin(dam_list)].reset_index(drop=True)

        # upstream controlled drainage area
        drainage_array = flowdir_object.basins(
            xy=(dam_gdf.geometry.x, dam_gdf.geometry.y),
            ids=dam_gdf[loc_col].astype('uint32')
        )
        drainage_shapes = rasterio.features.shapes(
            source=drainage_array.astype('int32'),
            mask=drainage_array != 0,
            transform=raster_profile['transform'],
            connectivity=8
        )
        drainage_features = [
            {'geometry': geometry, 'properties': {loc_col: value}} for geometry, value in drainage_shapes
        ]
        drainage_gdf = geopandas.GeoDataFrame.from_features(
            features=drainage_features,
            crs=raster_profile['crs']
        )
        drainage_gdf['area_m2'] = drainage_gdf.geometry.area

        # output dictionary
        output = {
            'dam_location_point': dam_gdf,
            'dam_drainage_polygon': drainage_gdf
        }

        # save the GeoDataFrames
        for key, gdf in output.items():
            geojson_file = os.path.join(folder_path, f'{key}.geojson')
            gdf.to_file(
                filename=geojson_file
            )

        return output
