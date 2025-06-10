import OptiDamTool
import tempfile
import os
import json
import pytest


@pytest.fixture(scope='class')
def watemsedem():

    yield OptiDamTool.WatemSedem()


@pytest.fixture
def message():

    output = {
        'error_folder': 'Input folder path is not valid.'
    }

    return output


def test_watemsedem(
    watemsedem
):

    # data folder
    data_folder = os.path.join(os.path.dirname(__file__), 'data')

    with tempfile.TemporaryDirectory() as tmp_dir:
        # dem to stream files required to run WaTEM/SEDEM
        output = watemsedem.dem_to_stream(
            dem_file=os.path.join(data_folder, 'dem.tif'),
            flwacc_percent=2,
            folder_path=tmp_dir
        )
        assert output == 'All required files has been generated'
        assert os.path.exists(os.path.join(tmp_dir, 'stream_lines.tif'))
        assert os.path.exists(os.path.join(tmp_dir, 'stream_routing.tif'))
        assert os.path.exists(os.path.join(tmp_dir, 'stream_lines.shp'))
        assert os.path.exists(os.path.join(tmp_dir, 'stream_adjacent_downstream_connectivity.txt'))
        assert not os.path.exists(os.path.join(tmp_dir, 'outlet_points.shp'))

        # read the summmary file
        with open(os.path.join(tmp_dir, 'summary.json')) as output_summary:
            summary_dict = json.load(output_summary)
        assert summary_dict['Number of valid DEM cells'] == 7862266
        assert summary_dict['Number of stream segments'] == 33
        assert summary_dict['Number of outlets'] == 1

        # dam effective drainage area shapefile
        output = watemsedem.dam_effective_drainage_polygon(
            flwdir_file=os.path.join(tmp_dir, 'flwdir.tif'),
            location_file=os.path.join(tmp_dir, 'subbasin_drainage_points.shp'),
            location_col='ws_id',
            dam_list=[21, 22, 5, 31, 17, 24, 27, 2, 13, 1],
            folder_path=tmp_dir
        )
        assert len(output) == 10
        assert output.loc[output['ws_id'] == 17, 'area_m2'].values[0] == 2978593200
        assert output.loc[output['ws_id'] == 31, 'area_m2'].values[0] == 175558500


def test_error_invalid_folder(
    watemsedem,
    message
):

    # dem to stream files required to run WaTEM/SEDEM
    with pytest.raises(Exception) as exc_info:
        watemsedem.dem_to_stream(
            dem_file='dem.tif',
            flwacc_percent=5,
            folder_path='output_folder'
        )
    assert exc_info.value.args[0] == message['error_folder']

    # dam effective drainage area shapefile
    with pytest.raises(Exception) as exc_info:
        watemsedem.dam_effective_drainage_polygon(
            flwdir_file='flwdir.tif',
            location_file='subbasin_drainage_points.shp',
            location_col='ws_id',
            dam_list=[1],
            folder_path='output_folder'
        )
    assert exc_info.value.args[0] == message['error_folder']


def test_github():

    assert str(2) == '2'
