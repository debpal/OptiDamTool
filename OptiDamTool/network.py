import GeoAnalyze
import pandas
import tempfile
import os


class Network:

    '''
    Provides functionality to establish network-based
    connectivity and operations between dams.
    '''

    def connectivity_adjacent(
        self,
        stream_file: str,
        stream_col: str,
        dam_list: list[int]
    ) -> dict[str, object]:

        '''
        Generates adjacent connectivity between dams based on the input stream network.
        Each dam is represented by a unique stream segment identifier.

        Returns a dictionary with two keys: 'downstream' and 'upstream'.

        - The value of 'downstream' is a dictionary where each key is a dam's stream identifier from
          the input `dam_list`, and the value is the adjacent downstream connected dam's stream identifier.
          A value of -1 indicates that the dam has no downstream connectivity.

        ..

        - The value of 'upstream' is a dictionary where each key is a dam's stream identifier from the
          `dam_list`, and the value is a list of adjacent upstream connected dam stream identifiers.
          An empty list indicates that the dam has no upstream connectivity.

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
            A dictionary with two keys, 'downstream' and 'upstream'. Each maps to a dictionary representing
            the adjacent downstream and upstream connectivity of dams, respectively, based on the stream network.
        '''

        # check distinct stream identifiers for dams
        if len(set(dam_list)) < len(dam_list):
            raise Exception('Duplicate stream identifiers found in the input dam list.')

        # temporary directory
        with tempfile.TemporaryDirectory() as tmp_dir:
            # connectivity from upstream to downstream
            connect_dict = GeoAnalyze.Stream().connectivity_upstream_to_downstream(
                stream_file=stream_file,
                stream_col=stream_col,
                json_file=os.path.join(tmp_dir, 'connectivity_upstream_to_downstream.json')
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
        adc_final = {
            k: v if k != v else -1 for k, v in adc_dict.items()
        }

        # DataFrame creation for adjacent downstream connectivity
        df = pandas.DataFrame(
            {
                'dam_id': adc_final.keys(),
                'adc_id': adc_final.values()
            }
        )

        # non-empty adjacent upstream connectivity
        auc_dict = {
            j: k['dam_id'].tolist() for j, k in df.groupby(by='adc_id')
        }

        # adjacent upstream connectivity of all dams
        auc_final = {
            i: auc_dict[i] if i in auc_dict else list() for i in dam_sorted
        }

        # output of all connectivity
        output = {
            'downstream': adc_final,
            'upstream': auc_final
        }

        return output
