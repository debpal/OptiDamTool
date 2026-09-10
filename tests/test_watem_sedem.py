import OptiDamTool
import rasterio
import tempfile
import os
import json
import pytest


@pytest.fixture(scope='class')
def watemsedem():

    yield OptiDamTool.WatemSedem()


def test_watemsedem(
    watemsedem
):

    # data folder
    data_folder = os.path.join(os.path.dirname(__file__), 'data')

    with tempfile.TemporaryDirectory() as tmp_dir:
        # Pass: dem to stream files
        output = watemsedem.dem_to_stream(
            dem_file=os.path.join(data_folder, 'dem.tif'),
            flwacc_percent=2,
            folder_path=tmp_dir
        )
        assert len(output) == 33
        assert os.path.exists(os.path.join(tmp_dir, 'stream_lines.tif'))
        assert os.path.exists(os.path.join(tmp_dir, 'stream_routing.tif'))
        assert os.path.exists(os.path.join(tmp_dir, 'stream_lines.shp'))
        assert os.path.exists(os.path.join(tmp_dir, 'stream_adjacent_downstream_connectivity.txt'))
        assert not os.path.exists(os.path.join(tmp_dir, 'outlet_points.shp'))
        with open(os.path.join(tmp_dir, 'summary.json')) as output_summary:
            summary_dict = json.load(output_summary)
        assert summary_dict['Number of valid DEM cells'] == 7862266
        assert summary_dict['Number of stream segments'] == 33
        assert summary_dict['Number of outlets'] == 1
        # Pass: raster with buffer region
        output = watemsedem.model_region_extension(
            dem_file=os.path.join(data_folder, 'dem.tif'),
            buffer_units=50,
            folder_path=tmp_dir
        )
        assert os.path.exists(os.path.join(tmp_dir, 'region.shp'))
        assert os.path.exists(os.path.join(tmp_dir, 'region_buffer.shp'))
        assert os.path.exists(os.path.join(tmp_dir, 'region_buffer.tif'))
        assert output['extended area (m^2)'] == 7806124800
        assert output['difference area (m^2)'] == 730085400
        # Pass: raster extension and NoData conversion
        output = watemsedem.raster_extension(
            input_file=os.path.join(tmp_dir, 'stream_lines.tif'),
            fill_value=0,
            region_file=os.path.join(tmp_dir, 'region_buffer.tif'),
            output_file=os.path.join(tmp_dir, 'stream_buffer.tif')
        )
        assert os.path.exists(os.path.join(tmp_dir, 'stream_buffer.tif'))
        assert output['dtype'] == 'int16'
        assert output['height'] == 3884
        assert output['width'] == 3517
        with rasterio.open(os.path.join(tmp_dir, 'stream_buffer.tif')) as input_raster:
            raster_array = input_raster.read(1)
            assert -9999 not in raster_array
            assert 0 in raster_array
        # Pass: constant raster
        output = watemsedem.raster_constant_extension(
            input_file=os.path.join(tmp_dir, 'region.tif'),
            constant_value=0.1694,
            region_file=os.path.join(tmp_dir, 'region.tif'),
            output_file=os.path.join(tmp_dir, 'RUSLE_K.tif'),
            dtype='float32'
        )
        assert os.path.exists(os.path.join(tmp_dir, 'RUSLE_K.tif'))
        assert output['dtype'] == 'float32'
        assert output['height'] == 3784
        assert output['width'] == 3417
        with rasterio.open(os.path.join(tmp_dir, 'RUSLE_K.tif')) as input_raster:
            raster_array = input_raster.read(1)
            assert -9999 not in raster_array
            assert 0 in raster_array
            assert 0.1694 in raster_array
        # Pass: raster clipping by bounding box
        output = watemsedem.raster_clipping_by_bounding_box(
            input_file=os.path.join(data_folder, 'R_clipped.tif'),
            shape_file=os.path.join(tmp_dir, 'region.shp'),
            output_file=os.path.join(tmp_dir, 'R_box.tif')
        )
        assert os.path.exists(os.path.join(tmp_dir, 'R_box.tif'))
        assert output['dtype'] == 'float32'
        assert output['height'] == 1155
        assert output['width'] == 1089
        with rasterio.open(os.path.join(tmp_dir, 'R_box.tif')) as input_raster:
            raster_array = input_raster.read(1)
            assert -9999 in raster_array
        # Pass: raster reprojection, cliiping, and rescaling
        output = watemsedem.raster_reproject_clipping_rescaling(
            input_file=os.path.join(tmp_dir, 'R_box.tif'),
            resampling_method='bilinear',
            shape_file=os.path.join(tmp_dir, 'region.shp'),
            mask_file=os.path.join(tmp_dir, 'region.tif'),
            output_file=os.path.join(tmp_dir, 'RUSLE_R.tif')
        )
        assert os.path.exists(os.path.join(tmp_dir, 'RUSLE_R.tif'))
        assert output['dtype'] == 'float32'
        assert output['height'] == 3784
        assert output['width'] == 3417
        with rasterio.open(os.path.join(tmp_dir, 'RUSLE_R.tif')) as input_raster:
            raster_array = input_raster.read(1)
            assert -9999 in raster_array
            assert round(raster_array.max()) == 167
        # Pass: multiplication of soil erodibility and rainfall erosivity factors
        output = watemsedem.rusle_kr(
            k_file=os.path.join(tmp_dir, 'RUSLE_K.tif'),
            r_file=os.path.join(tmp_dir, 'RUSLE_R.tif'),
            region_file=os.path.join(tmp_dir, 'region.tif'),
            output_file=os.path.join(tmp_dir, 'KR.tif'),
            k_multiplier=1000
        )
        with rasterio.open(os.path.join(tmp_dir, 'KR.tif')) as input_raster:
            raster_array = input_raster.read(1)
            assert -9999 in raster_array
            assert round(raster_array.max()) == 28252
        # Pass: land cover processing
        output = watemsedem.land_cover_esri(
            lc_file=os.path.join(data_folder, 'land_cover_clipped.tif'),
            stream_file=os.path.join(tmp_dir, 'stream_lines.shp'),
            folder_path=tmp_dir
        )
        assert os.path.exists(os.path.join(tmp_dir, 'land_cover_percent_esri.csv'))
        assert os.path.exists(os.path.join(tmp_dir, 'land_cover_cropland_unsplit.tif'))
        assert os.path.exists(os.path.join(tmp_dir, 'land_cover_percent_watemsedem.csv'))
        assert os.path.exists(os.path.join(tmp_dir, 'land_cover_extract_cropland.shp'))
        assert os.path.exists(os.path.join(tmp_dir, 'land_cover_cropland_split.tif'))
        assert output == 'Total agricultural lands identified: 1417'
        # Pass: land management factor
        output = watemsedem.land_management_factor(
            lc_file=os.path.join(data_folder, 'land_cover_clipped.tif'),
            stream_file=os.path.join(tmp_dir, 'stream_lines.shp'),
            output_file=os.path.join(tmp_dir, 'RUSLE_C.tif')
        )
        output == [0, 0.013, 0.22, 0.301, 0.374, 1]
        # Pass: raster driver conversion to Idrisi format
        output = watemsedem.raster_driver_to_rst(
            file_dict={
                'landuse': os.path.join(tmp_dir, 'land_cover_cropland_split.tif')
            },
            folder_path=tmp_dir
        )
        assert output == ['landuse.rst']
        assert os.path.exists(os.path.join(tmp_dir, 'landuse.rst'))


def test_github():

    assert str(2) == '2'
