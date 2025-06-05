import OptiDamTool
import tempfile
import os
import json
import pytest


@pytest.fixture(scope='class')
def watemsedem():

    yield OptiDamTool.WatemSedem()


def test_dem_to_stream(
    watemsedem
):

    # data folder
    data_folder = os.path.join(os.path.dirname(__file__), 'data')

    with tempfile.TemporaryDirectory() as tmp_dir:
        output = watemsedem.dem_to_stream(
            dem_file=os.path.join(data_folder, 'dem.tif'),
            flwacc_percent=5,
            folder_path=tmp_dir,
        )
        assert output == 'All required files has been generated'
        assert os.path.exists(os.path.join(tmp_dir, 'stream_lines.tif'))
        assert os.path.exists(os.path.join(tmp_dir, 'stream_routing.tif'))
        assert os.path.exists(os.path.join(tmp_dir, 'stream_lines.shp'))
        assert os.path.exists(os.path.join(tmp_dir, 'stream_adjacent_downstream_connectivity.txt'))
        assert not os.path.exists(os.path.join(tmp_dir, 'outlet_points.shp'))
        # open the summary file
        with open(os.path.join(tmp_dir, 'summary.json')) as output_summary:
            summary_dict = json.load(output_summary)
        assert summary_dict['Number of valid DEM cells'] == 7862266
        assert summary_dict['Number of stream segments'] == 13
        assert summary_dict['Number of outlets'] == 1

    # error test for invalid folder path
    with pytest.raises(Exception) as exc_info:
        watemsedem.dem_to_stream(
            dem_file='dem.tif',
            flwacc_percent=5,
            folder_path=tmp_dir
        )
    assert exc_info.value.args[0] == 'Input folder path is not valid.'


def test_github():

    assert str(1) == '1'
