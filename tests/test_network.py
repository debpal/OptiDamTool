import OptiDamTool
import pytest
import tempfile
import os


@pytest.fixture(scope='class')
def network():

    yield OptiDamTool.Network()


@pytest.fixture(scope='class')
def analysis():

    yield OptiDamTool.Analysis()


def test_netwrok(
    network,
    analysis
):

    # data folder
    data_folder = os.path.join(os.path.dirname(__file__), 'data')

    with tempfile.TemporaryDirectory() as tmp_dir:
        # adjacent downstream connectivity
        output = network.connectivity_adjacent_downstream(
            stream_file=os.path.join(data_folder, 'stream_lines.shp'),
            stream_col='ws_id',
            dam_list=[21, 22, 5, 31, 17, 24, 27, 2, 13, 1]
        )
        assert output[17] == 21
        assert output[31] == -1
        # adjacent upstream connectivity
        output = network.connectivity_adjacent_upstream(
            stream_file=os.path.join(data_folder, 'stream_lines.shp'),
            stream_col='ws_id',
            dam_list=[21, 22, 5, 31, 17, 24, 27, 2, 13, 1],
            sort_dam=True
        )
        assert output[17] == [1, 2, 5, 13]
        assert output[31] == []
        # effective upstream drainage area
        output = network.effective_drainage_area(
            stream_file=os.path.join(data_folder, 'stream_lines.shp'),
            stream_col='ws_id',
            dam_list=[21, 22, 5, 31, 17, 24, 27, 2, 13, 1]
        )
        assert output[17] == 2978593200
        assert output[31] == 175558500
        # sediment delivery to stream
        output = analysis.sediment_delivery_to_stream_txt(
            input_file=os.path.join(data_folder, 'stream_information.txt'),
            stream_col='ws_id',
            segsed_file=os.path.join(data_folder, 'Total sediment segments.txt'),
            cumsed_file=os.path.join(data_folder, 'Cumulative sediment segments.txt'),
            output_file=os.path.join(tmp_dir, 'stream_sediment_delivery.txt')
        )
        assert output.shape == (33, 7)
        # stream information shapefile
        output = analysis.sediment_delivery_to_stream_shapefile(
            stream_file=os.path.join(data_folder, 'stream_lines.shp'),
            sediment_file=os.path.join(tmp_dir, 'stream_sediment_delivery.txt'),
            output_file=os.path.join(tmp_dir, 'stream_sediment_delivery.shp')
        )
        assert output.shape == (33, 10)
        # effective sediment inflow
        output = network.effective_sediment_inflow(
            stream_file=os.path.join(tmp_dir, 'stream_sediment_delivery.shp'),
            stream_col='ws_id',
            dam_list=[21, 22, 5, 31, 17, 24, 27, 2, 13, 1]
        )
        assert round(output[17]) == 534348713
        assert output[31] == 1292848
        # effective upstream metric summary
        output = network.effective_upstream_metrics_summary(
            stream_file=os.path.join(tmp_dir, 'stream_sediment_delivery.shp'),
            stream_col='ws_id',
            dam_list=[21, 22, 5, 31, 17, 24, 27, 2, 13, 1]
        )
        assert len(output) == 3
        assert 'adjacent_upstream_connection' in output
        assert 'effective_drainage_area_m2' in output
        assert 'effective_sediment_inflow_kg' in output
        assert 'adjacent_downstream_connection' not in output


def test_error_netwrok(
    network
):

    # data folder
    data_folder = os.path.join(os.path.dirname(__file__), 'data')

    # error for same stream identifiers in the input dam list
    with pytest.raises(Exception) as exc_info:
        network.connectivity_adjacent_downstream(
            stream_file=os.path.join(data_folder, 'stream_lines.shp'),
            stream_col='ws_id',
            dam_list=[21, 22, 5, 31, 31, 17, 24, 27, 2, 13, 1]
        )
    assert exc_info.value.args[0] == 'Duplicate stream identifiers found in the input dam list.'
    # error for invalid stream identifier
    with pytest.raises(Exception) as exc_info:
        network.connectivity_adjacent_upstream(
            stream_file=os.path.join(data_folder, 'stream_lines.shp'),
            stream_col='ws_id',
            dam_list=[21, 22, 5, 31, 17, 24, 27, 2, 13, 1, 34]
        )
    assert exc_info.value.args[0] == 'Invalid stream identifier 34 for a dam.'
