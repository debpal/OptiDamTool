import OptiDamTool
import pytest
import os


@pytest.fixture(scope='class')
def network():

    yield OptiDamTool.Network()


def test_netwrok(
    network
):

    # data folder
    data_folder = os.path.join(os.path.dirname(__file__), 'data')
    stream_file = os.path.join(data_folder, 'stream.shp')
    stream_col = 'ws_id'
    dam_list = [21, 22, 5, 31, 17, 24, 27, 2, 13, 1]

    # adjacent downstream connectivity
    output = network.connectivity_adjacent_downstream(
        stream_file=stream_file,
        stream_col=stream_col,
        dam_list=dam_list
    )
    assert output[17] == 21
    assert output[31] == -1
    # adjacent upstream connectivity
    output = network.connectivity_adjacent_upstream(
        stream_file=stream_file,
        stream_col=stream_col,
        dam_list=dam_list
    )
    assert output[17] == [1, 2, 5, 13]
    assert output[31] == []
    # effective upstream drainage area
    output = network.effective_drainage_area(
        stream_file=stream_file,
        stream_col=stream_col,
        info_file=os.path.join(data_folder, 'stream_information.txt'),
        dam_list=dam_list
    )
    assert output[17] == 2978593200
    assert output[31] == 175558500
    # effective sediment inflow
    output = network.effective_sediment_inflow(
        stream_file=os.path.join(data_folder, 'stream_info.shp'),
        stream_col='ws_id',
        dam_list=[21, 22, 5, 31, 17, 24, 27, 2, 13, 1]
    )
    assert round(output[17]) == 534348713
    assert output[31] == 1292848
    # effective upstream metric summary
    output = network.effective_upstream_metrics_summary(
        stream_file=os.path.join(data_folder, 'stream_info.shp'),
        stream_col='ws_id',
        dam_list=[21, 22, 5, 31, 17, 24, 27, 2, 13, 1]
    )
    assert len(output) == 3
    assert 'adjacent_upstream_connection' in output
    assert 'effective_drainage_area_m2' in output
    assert 'effective_sediment_inflow_kg' in output
    assert 'adjacent_downstream_connection' not in output
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
