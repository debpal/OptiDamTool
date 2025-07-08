import GeoAnalyze
import geopandas
import pandas
import typing


class Network:

    '''
    Provides functionality to establish network-based
    connectivity and operations between dams.
    '''

    def connectivity_adjacent_downstream(
        self,
        stream_file: str,
        stream_col: str,
        dam_list: list[int]
    ) -> dict[int, int]:

        '''
        Generates adjacent downstream connectivity between dams based on the input stream network.
        Each dam is represented by a unique stream segment identifier.

        Parameters
        ----------
        stream_file : str
            Path to the input stream shapefile.

        stream_col : str
            Column name in the stream shapefile containing
            a unique identifier for each stream segment.

        dam_list : list
            List of stream segment identifiers representing dam locations.

        Returns
        -------
        dict
            A dictionary with each key is a dam's stream identifier, and the corresponding value
            is the stream identifier of the directly connected downstream dam.
            A value of -1 indicates that the dam has no downstream connectivity.
        '''

        # check distinct stream identifiers for dams
        if len(set(dam_list)) < len(dam_list):
            raise Exception('Duplicate stream identifiers found in the input dam list.')

        # connectivity from upstream to downstream
        connect_dict = GeoAnalyze.Stream()._connectivity_upstream_to_downstream(
            stream_file=stream_file,
            stream_col=stream_col
        )

        # sort stream identifiers for dams
        dam_sorted = sorted(dam_list)

        # adjacent downstream connectvity
        adc_dict = {}
        for i in dam_sorted:
            if i not in connect_dict:
                raise Exception(f'Invalid stream identifier {i} for a dam.')
            # all dam connectivity towards outlet
            stream_connect = connect_dict[i]
            dam_connect = list(
                filter(lambda x: x in stream_connect, dam_list)
            )
            # if no downstream dam is found
            if len(dam_connect) == 0:
                adc_dict[i] = -1
            # extract the adjacent downstream dam
            else:
                dam_indices = [
                    stream_connect.index(j) for j in dam_connect
                ]
                adc_dict[i] = stream_connect[min(dam_indices)]

        # filtered connectivity for stream outlet identifiers where key and value are same
        output = {
            k: v if k != v else -1 for k, v in adc_dict.items()
        }

        return output

    def connectivity_adjacent_upstream(
        self,
        stream_file: str,
        stream_col: str,
        dam_list: list[int]
    ) -> dict[int, list[int]]:

        '''
        Computes adjacent upstream connectivity between dams based on the input stream network.
        Each dam is represented by a unique stream segment identifier.

        Parameters
        ----------
        stream_file : str
            Path to the input stream shapefile.

        stream_col : str
            Column name in the stream shapefile containing
            a unique identifier for each stream segment.

        dam_list : list
            List of stream segment identifiers representing dam locations.

        Returns
        -------
        dict
            A dictionary where each key is a dam's stream identifier, and the corresponding value
            is a list of adjacent upstream dam identifiers. An empty list indicates no upstream connectivity.
        '''

        # sort stream identifiers for dams
        dam_sorted = sorted(dam_list)

        # adjacent downstream connectivity dictionary
        adc_dict = self.connectivity_adjacent_downstream(
            stream_file=stream_file,
            stream_col=stream_col,
            dam_list=dam_sorted
        )

        # DataFrame creation for adjacent downstream connectivity
        df = pandas.DataFrame(
            {
                'dam_id': adc_dict.keys(),
                'adc_id': adc_dict.values()
            }
        )

        # non-empty adjacent upstream connectivity
        auc_dict = {
            j: k['dam_id'].tolist() for j, k in df.groupby(by='adc_id')
        }

        # adjacent upstream connectivity of all dams
        output = {
            i: auc_dict[i] if i in auc_dict else list() for i in dam_sorted
        }

        return output

    def effective_drainage_area(
        self,
        stream_file: str,
        stream_col: str,
        info_file: str,
        dam_list: list[int],
    ) -> dict[int, float]:

        '''
        Computes the effective upstream drainage area for selected dams
        based on their locations within the input stream network.
        Each dam is represented by a unique stream segment identifier.

        Parameters
        ----------
        stream_file : str
            Path to the input stream shapefile.

        stream_col : str
            Name of the column in the stream shapefile containing
            a unique identifier for each stream segment.

        info_file : str
            Path to the stream information text file ``stream_information.txt``,
            generated by :meth:`OptiDamTool.WatemSedem.dem_to_stream`.

        dam_list : list
            List of stream segment identifiers representing dam locations.

        Returns
        -------
        dict
            A dictionary where each key is a dam's stream segment identifier,
            and the corresponding value is the effective upstream drainage area in square meters.
        '''

        # sort stream identifiers for dams
        dam_sorted = sorted(dam_list)

        # adjacent downstream connectivity dictionary
        auc_dict = self.connectivity_adjacent_upstream(
            stream_file=stream_file,
            stream_col=stream_col,
            dam_list=dam_sorted
        )

        # cumulative area dictionary from stream information DataFrame
        si_df = pandas.read_csv(
            filepath_or_buffer=info_file,
            sep='\t'
        )
        cumarea_dict = dict(zip(si_df[stream_col], si_df['cumarea_m2']))

        # effective drainage area dictionary
        effdrain_dict = {}
        for i in dam_sorted:
            if len(auc_dict[i]) == 0:
                effdrain_dict[i] = cumarea_dict[i]
            else:
                upstream_area = sum(
                    [cumarea_dict[j] for j in auc_dict[i]]
                )
                effdrain_dict[i] = cumarea_dict[i] - upstream_area

        return effdrain_dict

    def effective_sediment_inflow(
        self,
        stream_file: str,
        stream_col: str,
        dam_list: list[int],
        sediment_col: str = 'cum_kg'
    ) -> dict[int, float]:

        '''
        Computes the effective sediment inflows for selected dams based on their
        locations within the input stream network. Each dam is identified by a
        unique stream segment identifier.

        Parameters
        ----------
        stream_file : str
            Path to the input stream information shapefile, generated by
            :meth:`OptiDamTool.Analysis.stream_information_shapefile`.

        stream_col : str
            Name of the column in the stream shapefile containing a unique
            identifier for each stream segment.

        dam_list : list
            List of stream segment identifiers representing dam locations.

        sediment_col : str, optional
            Name of the column (either ``cum_kg`` or ``cum_ton``) in the stream
            information shapefile that contains cumulative sediment input values
            for each stream segment. Default is ``cum_kg``.

        Returns
        -------
        dict
            A dictionary where each key is a dam's stream segment identifier,
            and the corresponding value is the effective sediment input in
            kilograms or tons, depending on the selected column.
        '''

        # sort stream identifiers for dams
        dam_sorted = sorted(dam_list)

        # adjacent downstream connectivity dictionary
        auc_dict = self.connectivity_adjacent_upstream(
            stream_file=stream_file,
            stream_col=stream_col,
            dam_list=dam_sorted
        )

        # cumulative sediment input from stream information GeoDataFrame
        stream_gdf = geopandas.read_file(stream_file)
        cumsed_dict = dict(zip(stream_gdf[stream_col], stream_gdf[sediment_col]))

        # effective sediment input dictionary
        effsed_dict = {}
        for i in dam_sorted:
            if len(auc_dict[i]) == 0:
                effsed_dict[i] = cumsed_dict[i]
            else:
                upstream_sediment = sum(
                    [cumsed_dict[j] for j in auc_dict[i]]
                )
                effsed_dict[i] = cumsed_dict[i] - upstream_sediment

        return effsed_dict

    def effective_upstream_metrics_summary(
        self,
        stream_file: str,
        stream_col: str,
        dam_list: list[int]
    ) -> dict[str, dict[int, typing.Any]]:

        '''
        Computes a summary of effective upstream metrics for selected dams based on their
        locations within the input stream network. Each dam is identified by a unique stream
        segment identifier.

        The function returns a dictionary containing three sub-dictionaries, where each key
        corresponds to a dam's stream identifier:

        - **adjacent_upstream_connections**: A dictionary where each value is a list of directly
          connected upstream dam identifiers. An empty list indicates no upstream connectivity.

        - **effective_drainage_area_m2**: A dictionary mapping each dam to its effective upstream
          drainage area in square meters, based on upstream dam connections.

        - **effective_sediment_inflow_kg**: A dictionary mapping each dam to its effective sediment
          inflow in kilograms, based on upstream dam connections.

        Parameters
        ----------
        stream_file : str
            Path to the input stream information shapefile, generated by
            :meth:`OptiDamTool.Analysis.stream_information_shapefile`.

        stream_col : str
            Name of the column in the stream shapefile containing a unique
            identifier for each stream segment.

        dam_list : list
            List of stream segment identifiers representing dam locations.

        Returns
        -------
        dict
            A dictionary with three keys: ``adjacent_upstream_connections``,
            ``effective_drainage_area_m2``, and ``effective_sediment_inflow_kg``.
            Each key maps to a sub-dictionary where the keys are dam segment identifiers
            and the values are the computed metrics.
        '''

        # sort stream identifiers for dams
        dam_sorted = sorted(dam_list)

        # adjacent downstream connectivity dictionary
        auc_dict = self.connectivity_adjacent_upstream(
            stream_file=stream_file,
            stream_col=stream_col,
            dam_list=dam_sorted
        )

        # stream information GeoDataFrame
        stream_gdf = geopandas.read_file(stream_file)

        # cumulative inputs dictionary
        cumarea_dict = dict(zip(stream_gdf[stream_col], stream_gdf['cum_m2']))
        cumsed_dict = dict(zip(stream_gdf[stream_col], stream_gdf['cum_kg']))

        # empty dictionary to store effective metrics
        effdrain_dict = {}
        effsed_dict = {}

        # effective metrics dictionary
        for i in dam_sorted:
            if len(auc_dict[i]) == 0:
                # effective drainage area for no upstream connection
                effdrain_dict[i] = cumarea_dict[i]
                # effective sediment inflow for no upstream connection
                effsed_dict[i] = cumsed_dict[i]
            else:
                # effective drainage area for upstream connections
                upstream_area = sum(
                    [cumarea_dict[j] for j in auc_dict[i]]
                )
                effdrain_dict[i] = cumarea_dict[i] - upstream_area
                # effective sediment inflow for upstream connections
                upstream_sediment = sum(
                    [cumsed_dict[j] for j in auc_dict[i]]
                )
                effsed_dict[i] = cumsed_dict[i] - upstream_sediment

        # output metric dictionary
        output = {
            'adjacent_upstream_connection': auc_dict,
            'effective_drainage_area_m2': effdrain_dict,
            'effective_sediment_inflow_kg': effsed_dict
        }

        return output
