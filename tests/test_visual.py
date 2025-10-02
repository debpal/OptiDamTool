import OptiDamTool
import pytest
import tempfile
import os


@pytest.fixture(scope='class')
def network():

    yield OptiDamTool.Network()


@pytest.fixture(scope='class')
def visual():

    yield OptiDamTool.Visual()


def test_visual(
    network,
    visual
):

    # data folder
    data_folder = os.path.join(os.path.dirname(__file__), 'data')

    # temporary direcotry
    with tempfile.TemporaryDirectory() as tmp_dir:

        # Pass: detailed version of storage dynamics for sedimentation and draiange scenarios
        output = network.stodym_plus_with_drainage_scenarios(
            stream_file=os.path.join(data_folder, 'stream_with_sediment.geojson'),
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

        # Pass: plot of sediment inflow to stream
        output = visual.sediment_inflow_to_stream(
            stream_file=os.path.join(data_folder, 'stream_with_sediment.geojson'),
            figure_file=os.path.join(tmp_dir, 'sediment_inflow_to_stream.png'),
            gui_window=False
        )
        assert os.path.exists(os.path.join(tmp_dir, 'sediment_inflow_to_stream.png'))
        assert sum([file.endswith('.png') for file in os.listdir(tmp_dir)]) == 1

        # Pass: plot of dam location in stream
        output = visual.dam_location_in_stream(
            stream_file=os.path.join(data_folder, 'stream_with_sediment.geojson'),
            dam_file=os.path.join(tmp_dir, 'year_0_dam_location_point.geojson'),
            figure_file=os.path.join(tmp_dir, 'dam_location_in_stream.png'),
            gui_window=False
        )
        assert os.path.exists(os.path.join(tmp_dir, 'dam_location_in_stream.png'))
        assert sum([file.endswith('.png') for file in os.listdir(tmp_dir)]) == 2

        # Pass: plot of dam system statistics
        output = visual.system_statistics(
            json_file=os.path.join(tmp_dir, 'system_statistics.json'),
            figure_file=os.path.join(tmp_dir, 'system_statistics.png'),
            gui_window=False
        )
        assert os.path.exists(os.path.join(tmp_dir, 'system_statistics.png'))
        assert sum([file.endswith('.png') for file in os.listdir(tmp_dir)]) == 3

        # Pass: plot of dam remaining storage
        output = visual.dam_individual_features(
            json_file=os.path.join(tmp_dir, 'dam_remaining_storage.json'),
            figure_file=os.path.join(tmp_dir, 'dam_remaining_storage.png'),
            gui_window=False
        )
        assert os.path.exists(os.path.join(tmp_dir, 'dam_remaining_storage.png'))
        assert sum([file.endswith('.png') for file in os.listdir(tmp_dir)]) == 4
