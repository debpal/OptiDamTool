import GeoAnalyze
import pandas


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
        Computes the effective upstream drainage area of selected dams based on the input stream network.
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

        # stream information DataFrame
        si_df = pandas.read_csv(
            filepath_or_buffer=info_file,
            sep='\t'
        )
        cumarea_dict = dict(zip(si_df[stream_col], si_df['cumarea_m2']))

        # effective drainage area dictionary
        area_dict = {}
        for i in dam_sorted:
            if len(auc_dict[i]) == 0:
                area_dict[i] = cumarea_dict[i]
            else:
                upstream_area = sum(
                    [cumarea_dict[j] for j in auc_dict[i]]
                )
                area_dict[i] = cumarea_dict[i] - upstream_area

        return area_dict
