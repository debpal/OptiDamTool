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
    stream_col = 'ws_id'

    with tempfile.TemporaryDirectory() as tmp_dir:
        # sediment delivery to stream
        output = analysis.sediment_delivery_to_stream_txt(
            input_file=os.path.join(data_folder, 'stream_information.txt'),
            stream_col=stream_col,
            sediment_file=os.path.join(data_folder, 'Total sediment segments.txt'),
            cumsed_file=os.path.join(data_folder, 'Cumulative sediment segments.txt'),
            output_file=os.path.join(tmp_dir, 'stream_sediment_delivery.txt')
        )
        assert output.shape == (33, 7)
        # stream information shapefile
        output = analysis.stream_information_shapefile(
            stream_file=os.path.join(data_folder, 'stream.shp'),
            info_file=os.path.join(tmp_dir, 'stream_sediment_delivery.txt'),
            output_file=os.path.join(tmp_dir, 'stream_info.shp')
        )
        assert output.shape == (33, 10)
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
