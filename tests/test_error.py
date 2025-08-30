import OptiDamTool
import pytest
import os


@pytest.fixture(scope='class')
def watemsedem():

    yield OptiDamTool.WatemSedem()


@pytest.fixture(scope='class')
def network():

    yield OptiDamTool.Network()


@pytest.fixture(scope='class')
def analysis():

    yield OptiDamTool.Analysis()


@pytest.fixture(scope='class')
def visual():

    yield OptiDamTool.Visual()


@pytest.fixture
def error_statement():

    output = {
        'type_folder_path': 'A valid string of folder_path must be provided when write_output is True',
        'value_folder_path': 'Input folder path is not valid',
        'type_ext_json': 'Output file path must have a valid JSON file extension',
        'type_ext_figure': 'Input figure_file extension ".pn" is not supported for saving the figure',
        'type_trap_equation': 'trap_equation must be a boolean, but got type "list"',
        'type_trap_constant': 'trap_constant must be a float when "trap_equation=False", but got type "NoneType"',
        'value_trap_constant': 'trap_constant 0.05 is invalid: must satisfy trap_threshold (0.1) < trap_constant < 1'
    }

    return output


def test_error_watemsedem(
    watemsedem,
    error_statement
):

    # dem to stream files required to run WaTEM/SEDEM
    with pytest.raises(Exception) as exc_info:
        watemsedem.dem_to_stream(
            dem_file='dem.tif',
            flwacc_percent=5,
            folder_path='no_folder'
        )
    assert exc_info.value.args[0] == error_statement['value_folder_path']

    # region boundary buffer raster
    with pytest.raises(Exception) as exc_info:
        watemsedem.model_region_extension(
            dem_file='dem.tif',
            buffer_units=50,
            folder_path='no_folder'
        )
    assert exc_info.value.args[0] == error_statement['value_folder_path']

    # land cover processing
    with pytest.raises(Exception) as exc_info:
        watemsedem.land_cover_esri(
            lc_file='lc.tif',
            stream_file='stream.shp',
            folder_path='no_folder'
        )
    assert exc_info.value.args[0] == error_statement['value_folder_path']

    # dam effective drainage area
    with pytest.raises(Exception) as exc_info:
        watemsedem.dam_controlled_drainage_polygons(
            flwdir_file='flwdir.tif',
            location_file='subbasin_drainage_points.shp',
            dam_list=[1],
            folder_path='no_folder'
        )
    assert exc_info.value.args[0] == error_statement['value_folder_path']


def test_error_netwrok(
    network,
    error_statement
):

    # data folder
    data_folder = os.path.join(os.path.dirname(__file__), 'data')

    # error for same stream identifiers in the input dam list
    with pytest.raises(Exception) as exc_info:
        network.connectivity_adjacent_downstream_dam(
            stream_file=os.path.join(data_folder, 'stream_lines.shp'),
            dam_list=[21, 22, 5, 31, 31, 17, 24, 27, 2, 13, 1]
        )
    assert exc_info.value.args[0] == 'Duplicate stream identifiers found in the input dam list'
    # error for invalid stream identifier
    with pytest.raises(Exception) as exc_info:
        network.connectivity_adjacent_upstream_dam(
            stream_file=os.path.join(data_folder, 'stream_lines.shp'),
            dam_list=[21, 22, 5, 31, 17, 24, 27, 2, 13, 1, 34]
        )
    assert exc_info.value.args[0] == 'Invalid stream identifier 34 for a dam'
    # error for mismatch of keys between storage and drainage area dictionaries
    with pytest.raises(Exception) as exc_info:
        network.trap_efficiency_brown(
            storage_dict={5: 1},
            area_dict={6: 1}
        )
    assert exc_info.value.args[0] == 'Mismatch of keys between two dictionaries'
    # error of absent folder path for storage dynamics lite version
    with pytest.raises(Exception) as exc_info:
        network.storage_dynamics_lite(
            stream_file='stream_sediment_delivery.shp',
            storage_dict={15: 2000000},
            year_limit=15,
            sediment_density=1300,
            write_output=True
        )
    assert exc_info.value.args[0] == error_statement['type_folder_path']
    # error of absent folder path for storage dynamics detailed version
    with pytest.raises(Exception) as exc_info:
        network.storage_dynamics_detailed(
            stream_file='stream_sediment_delivery.shp',
            storage_dict={15: 2000000},
            year_limit=15,
            sediment_density=1300,
            write_output=True
        )
    assert exc_info.value.args[0] == error_statement['type_folder_path']
    # error of invalid folder path for storage dynamics lite version
    with pytest.raises(Exception) as exc_info:
        network.storage_dynamics_lite(
            stream_file='stream_sediment_delivery.shp',
            storage_dict={15: 2000000},
            year_limit=15,
            sediment_density=1300,
            write_output=True,
            folder_path='tmp_dir'
        )
    assert exc_info.value.args[0] == error_statement['value_folder_path']
    # error of invalid folder path for storage dynamics detailed version
    with pytest.raises(Exception) as exc_info:
        network.storage_dynamics_detailed(
            stream_file='stream_sediment_delivery.shp',
            storage_dict={15: 2000000},
            year_limit=15,
            sediment_density=1300,
            write_output=True,
            folder_path='tmp_dir'
        )
    assert exc_info.value.args[0] == error_statement['value_folder_path']
    # error of invalid trap_equation type for storage dynamics detailed version
    with pytest.raises(Exception) as exc_info:
        network.storage_dynamics_detailed(
            stream_file='stream_sediment_delivery.shp',
            storage_dict={15: 2000000},
            year_limit=15,
            sediment_density=1300,
            trap_equation=[]
        )
    assert exc_info.value.args[0] == error_statement['type_trap_equation']
    # error of invalid trap_equation type for storage dynamics lite version
    with pytest.raises(Exception) as exc_info:
        network.storage_dynamics_lite(
            stream_file='stream_sediment_delivery.shp',
            storage_dict={15: 2000000},
            year_limit=15,
            sediment_density=1300,
            trap_equation=[]
        )
    assert exc_info.value.args[0] == error_statement['type_trap_equation']
    # error of invalid trap_equation type for storage dynamics detailed version
    with pytest.raises(Exception) as exc_info:
        network.storage_dynamics_detailed(
            stream_file='stream_sediment_delivery.shp',
            storage_dict={15: 2000000},
            year_limit=15,
            sediment_density=1300,
            trap_equation=False
        )
    assert exc_info.value.args[0] == error_statement['type_trap_constant']
    # error of invalid trap_equation type for storage dynamics lite version
    with pytest.raises(Exception) as exc_info:
        network.storage_dynamics_lite(
            stream_file='stream_sediment_delivery.shp',
            storage_dict={15: 2000000},
            year_limit=15,
            sediment_density=1300,
            trap_equation=False
        )
    assert exc_info.value.args[0] == error_statement['type_trap_constant']
    # error of invalid trap_equation value for storage dynamics detailed version
    with pytest.raises(Exception) as exc_info:
        network.storage_dynamics_detailed(
            stream_file='stream_sediment_delivery.shp',
            storage_dict={15: 2000000},
            year_limit=15,
            sediment_density=1300,
            trap_equation=False,
            trap_constant=0.05
        )
    assert exc_info.value.args[0] == error_statement['value_trap_constant']
    # error of invalid trap_equation value for storage dynamics lite version
    with pytest.raises(Exception) as exc_info:
        network.storage_dynamics_lite(
            stream_file='stream_sediment_delivery.shp',
            storage_dict={15: 2000000},
            year_limit=15,
            sediment_density=1300,
            trap_equation=False,
            trap_constant=0.05
        )
    assert exc_info.value.args[0] == error_statement['value_trap_constant']


def test_error_analysis(
    analysis,
    error_statement
):

    # error for JSON file extension
    with pytest.raises(Exception) as exc_info:
        analysis.sediment_delivery_to_stream_json(
            info_file='stream_information.txt',
            segsed_file='Total sediment segments.txt',
            cumsed_file='Cumulative sediment segments.txt',
            json_file='stream_sediment_delivery.txt'
        )
    assert exc_info.value.args[0] == error_statement['type_ext_json']
    with pytest.raises(Exception) as exc_info:
        analysis.sediment_summary_dynamics_region(
            sediment_file='Total sediment.txt',
            summary_file='summary.json',
            output_file='summary_total_sediment.txt'
        )
    assert exc_info.value.args[0] == error_statement['type_ext_json']
    # error for GeoJSON file extension
    with pytest.raises(Exception) as exc_info:
        analysis.sediment_delivery_to_stream_geojson(
            stream_file='stream_lines.shp',
            sediment_file='stream_sediment_delivery.txt',
            geojson_file='stream_sediment_delivery.shp'
        )
    assert exc_info.value.args[0] == 'Output file path must have a valid GeoJSON file extension'


def test_error_visual(
    visual,
    error_statement
):

    # error for invaid figure file extension for sediment inflow to stream
    with pytest.raises(Exception) as exc_info:
        visual.sediment_inflow_to_stream(
            stream_file='stream.geojson',
            figure_file='sediment_inflow_to_stream.pn'
        )
    assert exc_info.value.args[0] == error_statement['type_ext_figure']
    # error for invaid figure file extension for dam location in stream
    with pytest.raises(Exception) as exc_info:
        visual.dam_location_in_stream(
            stream_file='stream.geojson',
            dam_file='dam.geojson',
            figure_file='dam_location_in_stream.pn'
        )
    assert exc_info.value.args[0] == error_statement['type_ext_figure']
    # error for invaid figure file extension for dam remaining storage
    with pytest.raises(Exception) as exc_info:
        visual.dam_remaining_storage(
            json_file='dam_remaining_storage.json',
            figure_file='dam_remaining_storage.pn'
        )
    assert exc_info.value.args[0] == error_statement['type_ext_figure']
    # error for invaid figure file extension for dam trapped sediment
    with pytest.raises(Exception) as exc_info:
        visual.dam_trapped_sediment(
            json_file='dam_trapped_sediment.json',
            figure_file='dam_trapped_sediment.pn'
        )
    assert exc_info.value.args[0] == error_statement['type_ext_figure']
    # error for invaid figure file extension for dam trap efficiency
    with pytest.raises(Exception) as exc_info:
        visual.dam_trap_efficiency(
            json_file='dam_trap_efficiency.json',
            figure_file='dam_trap_efficiency.pn'
        )
    assert exc_info.value.args[0] == error_statement['type_ext_figure']
    # error for invaid figure file extension for system statistics
    with pytest.raises(Exception) as exc_info:
        visual.system_statistics(
            json_file='system_statistics.json',
            figure_file='system_statistics.pn'
        )
    assert exc_info.value.args[0] == error_statement['type_ext_figure']

    # error if all plot options are set to False for system statistics
    with pytest.raises(Exception) as exc_info:
        visual.system_statistics(
            json_file='system_statistics.json',
            figure_file='system_statistics.png',
            plot_storage=False,
            plot_trap=False,
            plot_release=False,
            plot_drainage=False
        )
    assert exc_info.value.args[0] == 'At least one plot type must be set to True'
