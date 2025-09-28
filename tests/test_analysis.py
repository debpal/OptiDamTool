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
        # Pass: summary of total sediment dynamics
        output = analysis.sediment_summary_dynamics_region(
            sediment_file=os.path.join(data_folder, 'Total sediment.txt'),
            summary_file=os.path.join(data_folder, 'summary.json'),
            output_file=os.path.join(tmp_dir, 'summary_total_sediment.json')
        )
        assert output.shape == (4, 6)
        assert os.path.exists(os.path.join(tmp_dir, 'summary_total_sediment.json'))
        # Pass: retrieve raster features
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
        # Pass: private function for dam extraction features
        output = analysis._dam_features_extraction(
            input_file=os.path.join(data_folder, 'dam_features_sample.geojson'),
            output_file=os.path.join(tmp_dir, 'dam_features_extracted.geojson')
        )
        assert output.shape == (6, 19)
