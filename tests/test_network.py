import os
import OptiDamTool
import pytest


@pytest.fixture(scope='class')
def network():

    yield OptiDamTool.Network()


def test_connectivity(
    network
):

    # data folder
    data_folder = os.path.join(os.path.dirname(__file__), 'data')

    # adjacent downstream connectivity
    output = network.connectivity_adjacent_downstream(
        stream_file=os.path.join(data_folder, 'stream.shp'),
        stream_col='ws_id',
        dam_list=[21, 22, 5, 31, 17, 24, 27, 2, 13, 1]
    )
    assert output[17] == 21
    assert output[31] == -1

    # adjacent upstream connectivity
    output = network.connectivity_adjacent_upstream(
        stream_file=os.path.join(data_folder, 'stream.shp'),
        stream_col='ws_id',
        dam_list=[21, 22, 5, 31, 17, 24, 27, 2, 13, 1]
    )
    assert output[17] == [1, 2, 5, 13]
    assert output[31] == []

    # error for same stream identifiers in the input dam list
    with pytest.raises(Exception) as exc_info:
        network.connectivity_adjacent_downstream(
            stream_file=os.path.join(data_folder, 'stream.shp'),
            stream_col='ws_id',
            dam_list=[21, 22, 5, 31, 31, 17, 24, 27, 2, 13, 1]
        )
    assert exc_info.value.args[0] == 'Duplicate stream identifiers found in the input dam list.'

    # error for invalid stream identifier
    with pytest.raises(Exception) as exc_info:
        network.connectivity_adjacent_upstream(
            stream_file=os.path.join(data_folder, 'stream.shp'),
            stream_col='ws_id',
            dam_list=[21, 22, 5, 31, 17, 24, 27, 2, 13, 1, 34]
        )
    assert exc_info.value.args[0] == 'Invalid stream identifier 34 for a dam.'
