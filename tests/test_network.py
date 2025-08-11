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


@pytest.fixture
def message():

    output = {
        'error_folder': 'Input folder path is not valid.',
        'error_folder_type': 'A valid string of folder_path must be provided when write_output is True.'
    }

    return output


def test_netwrok(
    network,
    analysis
):

    # data folder
    data_folder = os.path.join(os.path.dirname(__file__), 'data')

    with tempfile.TemporaryDirectory() as tmp_dir:
        # adjacent downstream connectivity
        output = network.connectivity_adjacent_downstream_dam(
            stream_file=os.path.join(data_folder, 'stream_lines.shp'),
            stream_col='ws_id',
            dam_list=[21, 22, 5, 31, 17, 24, 27, 2, 13, 1]
        )
        assert output[17] == 21
        assert output[31] == -1
        # adjacent upstream connectivity
        output = network.connectivity_adjacent_upstream_dam(
            stream_file=os.path.join(data_folder, 'stream_lines.shp'),
            stream_col='ws_id',
            dam_list=[21, 22, 5, 31, 17, 24, 27, 2, 13, 1],
            sort_dam=True
        )
        assert output[17] == [1, 2, 5, 13]
        assert output[31] == []
        # controlled drainage area
        output = network.controlled_drainage_area(
            stream_file=os.path.join(data_folder, 'stream_lines.shp'),
            stream_col='ws_id',
            dam_list=[21, 22, 5, 31, 17, 24, 27, 2, 13, 1]
        )
        assert output[17] == 2978593200
        assert output[31] == 175558500
        # sediment delivery to stream
        output = analysis.sediment_delivery_to_stream_json(
            info_file=os.path.join(data_folder, 'stream_information.json'),
            stream_col='ws_id',
            segsed_file=os.path.join(data_folder, 'Total sediment segments.txt'),
            cumsed_file=os.path.join(data_folder, 'Cumulative sediment segments.txt'),
            json_file=os.path.join(tmp_dir, 'stream_sediment_delivery.json')
        )
        assert output.shape == (33, 7)
        assert os.path.exists(os.path.join(tmp_dir, 'stream_sediment_delivery.json'))
        # stream information shapefile
        output = analysis.sediment_delivery_to_stream_geojson(
            stream_file=os.path.join(data_folder, 'stream_lines.shp'),
            sediment_file=os.path.join(tmp_dir, 'stream_sediment_delivery.json'),
            geojson_file=os.path.join(tmp_dir, 'stream_sediment_delivery.geojson')
        )
        assert output.shape == (33, 10)
        assert os.path.exists(os.path.join(tmp_dir, 'stream_sediment_delivery.geojson'))
        # sediment inflow from drainage area
        output = network.sediment_inflow_from_drainage_area(
            stream_file=os.path.join(tmp_dir, 'stream_sediment_delivery.geojson'),
            stream_col='ws_id',
            dam_list=[21, 22, 5, 31, 17, 24, 27, 2, 13, 1]
        )
        assert round(output[17]) == 534348713
        assert output[31] == 1292848
        # upstream metric summary of dams
        output = network.upstream_metrics_summary(
            stream_file=os.path.join(tmp_dir, 'stream_sediment_delivery.geojson'),
            stream_col='ws_id',
            dam_list=[21, 22, 5, 31, 17, 24, 27, 2, 13, 1]
        )
        assert len(output) == 3
        assert 'adjacent_upstream_dams' in output
        assert 'controlled_drainage_m2' in output
        assert 'sediment_inflow_kg' in output
        assert 'adjacent_downstream_connection' not in output
        assert output['adjacent_upstream_dams'][17] == [5, 2, 13, 1]
        assert output['controlled_drainage_m2'][17] == 2978593200
        assert round(output['sediment_inflow_kg'][17]) == 534348713
        # lite version of storage dynamics for sedimentation
        output = network.storage_dynamics_lite(
            stream_file=os.path.join(tmp_dir, 'stream_sediment_delivery.geojson'),
            stream_col='ws_id',
            storage_dict={
                21: 1500000,
                5: 100000,
                24: 60000,
                27: 200000,
                33: 1000000,
            },
            year_limit=15,
            sediment_density=1300,
            trap_threshold=0.05,
            write_output=True,
            folder_path=tmp_dir
        )
        assert len(output) == 5
        # detailed version of storage dynamics for sedimentation
        output = network.storage_dynamics_and_drainage_scenarios(
            stream_file=os.path.join(tmp_dir, 'stream_sediment_delivery.geojson'),
            stream_col='ws_id',
            flwdir_file=os.path.join(data_folder, 'flwdir.tif'),
            storage_dict={
                21: 1500000,
                5: 100000,
                24: 60000,
                27: 200000,
                33: 1000000,
            },
            year_limit=15,
            sediment_density=1300,
            trap_threshold=0.05,
            folder_path=tmp_dir
        )
        assert output.shape == (10, 3)
        scenario_files = [i for i in os.listdir(tmp_dir) if i.startswith('year_') and i.endswith('.geojson')]
        assert len(scenario_files) == 10


def test_error_netwrok(
    network,
    message
):

    # data folder
    data_folder = os.path.join(os.path.dirname(__file__), 'data')

    # error for same stream identifiers in the input dam list
    with pytest.raises(Exception) as exc_info:
        network.connectivity_adjacent_downstream_dam(
            stream_file=os.path.join(data_folder, 'stream_lines.shp'),
            stream_col='ws_id',
            dam_list=[21, 22, 5, 31, 31, 17, 24, 27, 2, 13, 1]
        )
    assert exc_info.value.args[0] == 'Duplicate stream identifiers found in the input dam list.'
    # error for invalid stream identifier
    with pytest.raises(Exception) as exc_info:
        network.connectivity_adjacent_upstream_dam(
            stream_file=os.path.join(data_folder, 'stream_lines.shp'),
            stream_col='ws_id',
            dam_list=[21, 22, 5, 31, 17, 24, 27, 2, 13, 1, 34]
        )
    assert exc_info.value.args[0] == 'Invalid stream identifier 34 for a dam.'
    # error for mismatch of keys between storage and drainage area dictionaries
    with pytest.raises(Exception) as exc_info:
        network.trap_efficiency_brown(
            storage_dict={5: 1},
            area_dict={6: 1}
        )
    assert exc_info.value.args[0] == 'Mismatch of keys between two dictionaries.'
    # error of absent folder path for storage dynamics lite version
    with pytest.raises(Exception) as exc_info:
        network.storage_dynamics_lite(
            stream_file='stream_sediment_delivery.shp',
            stream_col='ws_id',
            storage_dict={15: 2000000},
            year_limit=15,
            sediment_density=1300,
            trap_threshold=0.05,
            write_output=True
        )
    assert exc_info.value.args[0] == message['error_folder_type']
    # error of absent folder path for storage dynamics detailed version
    with pytest.raises(Exception) as exc_info:
        network.storage_dynamics_detailed(
            stream_file='stream_sediment_delivery.shp',
            stream_col='ws_id',
            storage_dict={15: 2000000},
            year_limit=15,
            sediment_density=1300,
            trap_threshold=0.05,
            write_output=True
        )
    assert exc_info.value.args[0] == message['error_folder_type']
    # error of invalid folder path for storage dynamics lite version
    with pytest.raises(Exception) as exc_info:
        network.storage_dynamics_lite(
            stream_file='stream_sediment_delivery.shp',
            stream_col='ws_id',
            storage_dict={15: 2000000},
            year_limit=15,
            sediment_density=1300,
            trap_threshold=0.05,
            write_output=True,
            folder_path='tmp_dir'
        )
    assert exc_info.value.args[0] == message['error_folder']
    # error of invalid folder path for storage dynamics detailed version
    with pytest.raises(Exception) as exc_info:
        network.storage_dynamics_detailed(
            stream_file='stream_sediment_delivery.shp',
            stream_col='ws_id',
            storage_dict={15: 2000000},
            year_limit=15,
            sediment_density=1300,
            trap_threshold=0.05,
            write_output=True,
            folder_path='tmp_dir'
        )
    assert exc_info.value.args[0] == message['error_folder']
