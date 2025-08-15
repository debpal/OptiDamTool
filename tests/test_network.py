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


@pytest.fixture(scope='class')
def visual():

    yield OptiDamTool.Visual()


def test_netwrok(
    network,
    analysis,
    visual
):

    # data folder
    data_folder = os.path.join(os.path.dirname(__file__), 'data')

    with tempfile.TemporaryDirectory() as tmp_dir:
        # adjacent downstream connectivity
        output = network.connectivity_adjacent_downstream_dam(
            stream_file=os.path.join(data_folder, 'stream_lines.shp'),
            dam_list=[21, 22, 5, 31, 17, 24, 27, 2, 13, 1]
        )
        assert output[17] == 21
        assert output[31] == -1
        # adjacent upstream connectivity
        output = network.connectivity_adjacent_upstream_dam(
            stream_file=os.path.join(data_folder, 'stream_lines.shp'),
            dam_list=[21, 22, 5, 31, 17, 24, 27, 2, 13, 1],
            sort_dam=True
        )
        assert output[17] == [1, 2, 5, 13]
        assert output[31] == []
        # controlled drainage area
        output = network.controlled_drainage_area(
            stream_file=os.path.join(data_folder, 'stream_lines.shp'),
            dam_list=[21, 22, 5, 31, 17, 24, 27, 2, 13, 1]
        )
        assert output[17] == 2978593200
        assert output[31] == 175558500
        # sediment delivery to stream
        output = analysis.sediment_delivery_to_stream_json(
            info_file=os.path.join(data_folder, 'stream_information.json'),
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
            dam_list=[21, 22, 5, 31, 17, 24, 27, 2, 13, 1]
        )
        assert round(output[17]) == 534348713
        assert output[31] == 1292848
        # upstream metric summary of dams
        output = network.upstream_metrics_summary(
            stream_file=os.path.join(tmp_dir, 'stream_sediment_delivery.geojson'),
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
        # plot of dam location in stream
        output = visual.dam_location_in_stream(
            stream_file=os.path.join(tmp_dir, 'stream_sediment_delivery.geojson'),
            dam_file=os.path.join(tmp_dir, 'year_0_dam_location_point.geojson'),
            figure_file=os.path.join(tmp_dir, 'dam_location_in_stream.png'),
            gui_window=False
        )
        assert os.path.exists(os.path.join(tmp_dir, 'dam_location_in_stream.png'))
        assert sum([file.endswith('.png') for file in os.listdir(tmp_dir)]) == 1
        # plot of dam remaining storage
        output = visual.dam_remaining_storage(
            json_file=os.path.join(tmp_dir, 'dam_remaining_storage.json'),
            figure_file=os.path.join(tmp_dir, 'dam_remaining_storage.png'),
            gui_window=False
        )
        assert os.path.exists(os.path.join(tmp_dir, 'dam_remaining_storage.png'))
        assert sum([file.endswith('.png') for file in os.listdir(tmp_dir)]) == 2
        # plot of dam sediment trapping
        output = visual.dam_trapped_sediment(
            json_file=os.path.join(tmp_dir, 'dam_trapped_sediment.json'),
            figure_file=os.path.join(tmp_dir, 'dam_trapped_sediment.png'),
            gui_window=False
        )
        assert os.path.exists(os.path.join(tmp_dir, 'dam_trapped_sediment.png'))
        assert sum([file.endswith('.png') for file in os.listdir(tmp_dir)]) == 3
        # plot of dam system statistics
        output = visual.system_statistics(
            json_file=os.path.join(tmp_dir, 'system_statistics.json'),
            figure_file=os.path.join(tmp_dir, 'system_statistics.png'),
            gui_window=False
        )
        assert os.path.exists(os.path.join(tmp_dir, 'system_statistics.png'))
        assert sum([file.endswith('.png') for file in os.listdir(tmp_dir)]) == 4
