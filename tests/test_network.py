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
def system_design():

    yield OptiDamTool.SystemDesign()


def test_netwrok(
    network,
    analysis,
    system_design
):

    # data folder
    data_folder = os.path.join(os.path.dirname(__file__), 'data')

    with tempfile.TemporaryDirectory() as tmp_dir:

        # Pass: adjacent downstream connectivity
        output = network.connectivity_adjacent_downstream_dam(
            stream_file=os.path.join(data_folder, 'stream_lines.shp'),
            dam_list=[21, 22, 5, 31, 17, 24, 27, 2, 13, 1]
        )
        assert output[17] == 21
        assert output[31] == -1

        # Pass: adjacent upstream connectivity
        output = network.connectivity_adjacent_upstream_dam(
            stream_file=os.path.join(data_folder, 'stream_lines.shp'),
            dam_list=[21, 22, 5, 31, 17, 24, 27, 2, 13, 1],
            sort_dam=True
        )
        assert output[17] == [1, 2, 5, 13]
        assert output[31] == []

        # Pass: controlled drainage area
        output = network.controlled_drainage_area(
            stream_file=os.path.join(data_folder, 'stream_lines.shp'),
            dam_list=[21, 22, 5, 31, 17, 24, 27, 2, 13, 1]
        )
        assert output[17] == 2978593200
        assert output[31] == 175558500

        # Pass: sediment delivery to stream
        output = analysis.sediment_delivery_to_stream_json(
            info_file=os.path.join(data_folder, 'stream_information.json'),
            segsed_file=os.path.join(data_folder, 'Total sediment segments.txt'),
            cumsed_file=os.path.join(data_folder, 'Cumulative sediment segments.txt'),
            json_file=os.path.join(tmp_dir, 'stream_sediment_delivery.json')
        )
        assert output.shape == (33, 7)
        assert os.path.exists(os.path.join(tmp_dir, 'stream_sediment_delivery.json'))

        # Pass: stream information shapefile
        output = analysis.sediment_delivery_to_stream_geojson(
            stream_file=os.path.join(data_folder, 'stream_lines.shp'),
            sediment_file=os.path.join(tmp_dir, 'stream_sediment_delivery.json'),
            geojson_file=os.path.join(tmp_dir, 'stream_sediment_delivery.geojson')
        )
        assert output.shape == (33, 10)
        assert os.path.exists(os.path.join(tmp_dir, 'stream_sediment_delivery.geojson'))

        # Pass: sediment inflow from drainage area
        output = network.sediment_inflow_from_drainage_area(
            stream_file=os.path.join(tmp_dir, 'stream_sediment_delivery.geojson'),
            dam_list=[21, 22, 5, 31, 17, 24, 27, 2, 13, 1]
        )
        assert round(output[17]) == 534348713
        assert output[31] == 1292848

        # Pass: upstream metric summary of dams
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

        # storage dictionary
        storage_dict = {
            21: 1500000,
            5: 100000,
            24: 60000,
            27: 200000,
            33: 1000000,
        }

        # Pass: storage dynamics for sedimentation with constant trap efficiency
        output = network.stodym_plus(
            stream_file=os.path.join(tmp_dir, 'stream_sediment_delivery.geojson'),
            storage_dict=storage_dict,
            year_limit=15,
            sediment_density=1300,
            trap_equation=False,
            trap_threshold=0.05,
            trap_constant=0.8,
            folder_path=tmp_dir
        )
        assert isinstance(output, dict)
        assert len(output) == 7
        assert output['dam_lifespan']['life_year'].tolist() == [3, 2, 5, 4, 5]
