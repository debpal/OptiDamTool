import OptiDamTool
import pytest
import rasterio
import tempfile
import os


@pytest.fixture(scope='class')
def analysis():

    yield OptiDamTool.Analysis()


def test_analysis(
    analysis
):

    # data folder
    data_folder = os.path.join(os.path.dirname(__file__), 'data')

    with tempfile.TemporaryDirectory() as tmp_dir:
        # summary of total sediment dynamics
        output = analysis.sediment_summary_dynamics_region(
            input_file=os.path.join(data_folder, 'Total sediment.txt'),
            json_file=os.path.join(data_folder, 'summary.json'),
            output_file=os.path.join(tmp_dir, 'summary_total_sediment_dynamics.txt')
        )
        assert output.shape == (4, 6)
        # raster features retrieve
        output = analysis.raster_features_retrieve(
            input_file=os.path.join(data_folder, 'WATEREROS_kg.rst'),
            crs_code=32638,
            output_file=os.path.join(tmp_dir, 'WATEREROS_ton.tif'),
            scale=.001
        )
        assert output == 'All geoprocessing steps are complete'
        with rasterio.open(os.path.join(tmp_dir, 'WATEREROS_ton.tif')) as input_raster:
            raster_array = input_raster.read(1)
            assert round(raster_array.max()) == 217735
