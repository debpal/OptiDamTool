import OptiDamTool
import pytest
import os
import tempfile


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


@pytest.fixture(scope='class')
def system_design():

    yield OptiDamTool.SystemDesign()


@pytest.fixture
def error_statement():

    output = {
        'value_folder_path': 'Input folder_path is not valid',
        'type_ext_json': 'Output file path must have a valid JSON file extension',
        'type_ext_figure': 'Input figure_file extension ".pn" is not supported for saving the figure'
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
    assert exc_info.value.args[0] == 'Mismatch of keys between storage and area dictionaries'

    # error of invalid folder path for storage dynamics lite version
    with pytest.raises(Exception) as exc_info:
        network.storage_dynamics_lite(
            stream_file='stream_sediment_delivery.shp',
            storage_dict={15: 2000000},
            year_limit=15,
            sediment_density=1300,
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
            folder_path='tmp_dir'
        )
    assert exc_info.value.args[0] == error_statement['value_folder_path']

    # error of invalid variable type which is not union
    with pytest.raises(Exception) as exc_info:
        network.storage_dynamics_detailed(
            stream_file='stream_sediment_delivery.shp',
            storage_dict={15: 2000000},
            year_limit=15,
            sediment_density=1300,
            trap_equation=[]
        )
    assert exc_info.value.args[0] == 'Expected "trap_equation" to be "bool", but got type "list"'

    # error of invalid trap_equation type for storage dynamics detailed version
    typ_args = ['str', 'NoneType']
    with pytest.raises(Exception) as exc_info:
        network.storage_dynamics_detailed(
            stream_file='stream_sediment_delivery.shp',
            storage_dict={15: 2000000},
            year_limit=15,
            sediment_density=1300,
            folder_path=1
        )
    assert exc_info.value.args[0] == f'Expected "folder_path" to be one of {typ_args}, but got type "int"'

    # error of invalid storage_dict for storage dynamics lite version
    with pytest.raises(Exception) as exc_info:
        network.storage_dynamics_lite(
            stream_file='stream_sediment_delivery.shp',
            storage_dict={15: -10},
            year_limit=15,
            sediment_density=1300
        )
    assert exc_info.value.args[0] == 'Invalid negative intial storage volume -10 for the dam identifier 15 was received'

    # error of invalid year_limit for storage dynamics lite version
    with pytest.raises(Exception) as exc_info:
        network.storage_dynamics_lite(
            stream_file='stream_sediment_delivery.shp',
            storage_dict={15: 2000000},
            year_limit=-1,
            sediment_density=1300
        )
    assert exc_info.value.args[0] == 'year_limit must be greater than 0, but received -1'

    # error of invalid trap_constant type when trap_equation=False for storage dynamics lite version
    with pytest.raises(Exception) as exc_info:
        network.storage_dynamics_lite(
            stream_file='stream_sediment_delivery.shp',
            storage_dict={15: 2000000},
            year_limit=15,
            sediment_density=1300,
            trap_equation=False
        )
    assert exc_info.value.args[0] == 'trap_constant must be a numeric value when "trap_equation=False", but got type "NoneType"'

    # error of invalid trap_constant value for storage dynamics lite version
    with pytest.raises(Exception) as exc_info:
        network.storage_dynamics_lite(
            stream_file='stream_sediment_delivery.shp',
            storage_dict={15: 2000000},
            year_limit=15,
            sediment_density=1300,
            trap_equation=False,
            trap_constant=0.05
        )
    assert exc_info.value.args[0] == 'trap_constant 0.05 is invalid: must satisfy trap_threshold (0.1) < trap_constant <= 1'


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


def test_error_systemdesign(
    system_design,
    error_statement
):

    # data folder
    data_folder = os.path.join(os.path.dirname(__file__), 'data')

    # input varilables
    dam_number = 5
    storage_bounds = (1, 50)
    storage_multiplier = 50000
    stream_file = 'stream_with_sediment.geojson'
    model_config = {
        'sediment_density': 1300,
        'year_limit': 100
    }
    objectives = [
        'lifespan',
    ]
    algorithm_name = 'NSGAII'
    algorithm_config = {
        'population_size': 10
    }
    nfe = 50
    seeds = 2
    sorting_methods = [
        'by_objective_directions',
        'by_dam_idenfiers',
        'by_metric_euclidean'
    ]
    valid_modelconfig = [
        'sediment_density',
        'year_limit',
        'trap_equation',
        'trap_threshold',
        'brown_d',
        'trap_constant',
        'release_threshold'
    ]
    valid_algorithms = ['NSGAII']
    valid_algorithmargs = [
        'population_size',
        'generator',
        'selector',
        'variator',
        'archive'
    ]
    valid_objectives = list(system_design.mapping_objective_direction.keys())
    valid_constraints = list(system_design.mapping_constraint_operator.keys())

    # error for sedimentation management by genetic algorithm
    with tempfile.TemporaryDirectory() as tmp_dir:
        # error for invaid folder path
        with pytest.raises(Exception) as exc_info:
            system_design.solution_sedimentation_management_by_ga(
                dam_number=dam_number,
                storage_bounds=storage_bounds,
                storage_multiplier=storage_multiplier,
                stream_file=stream_file,
                model_config=model_config,
                objectives=objectives,
                algorithm_name=algorithm_name,
                algorithm_config=algorithm_config,
                seeds=seeds,
                nfe=nfe,
                folder_path='tmp_dir'
            )
        assert exc_info.value.args[0] == error_statement['value_folder_path']
        # error for invaid seed number
        with pytest.raises(Exception) as exc_info:
            system_design.solution_sedimentation_management_by_ga(
                dam_number=dam_number,
                storage_bounds=storage_bounds,
                storage_multiplier=storage_multiplier,
                stream_file=stream_file,
                model_config=model_config,
                objectives=objectives,
                algorithm_name=algorithm_name,
                algorithm_config=algorithm_config,
                seeds=-2,
                nfe=nfe,
                folder_path=tmp_dir
            )
        assert exc_info.value.args[0] == 'Input seeds must be greater than or equal to 1, but received -2'
        # error for invaid sorting method name
        with pytest.raises(Exception) as exc_info:
            system_design.solution_sedimentation_management_by_ga(
                dam_number=dam_number,
                storage_bounds=storage_bounds,
                storage_multiplier=storage_multiplier,
                stream_file=stream_file,
                model_config=model_config,
                objectives=objectives,
                algorithm_name=algorithm_name,
                algorithm_config=algorithm_config,
                seeds=seeds,
                nfe=nfe,
                folder_path=tmp_dir,
                solution_sorting='by_metric_none'
            )
        assert exc_info.value.args[0] == f'Invalid solution_sorting name "by_metric_none"; valid names are {sorting_methods}'

    # error test for storage_bounds length greater than 2
    with pytest.raises(Exception) as exc_info:
        system_design._validate_variable_config(
            stream_file=os.path.join(data_folder, 'stream_with_sediment.geojson'),
            dam_number=dam_number,
            storage_bounds=(1, 50, 100),
            storage_multiplier=storage_multiplier
        )
    assert exc_info.value.args[0] == 'storage_bounds must contain exactly 2 integers, but received 3 elements'

    # error test for invalid value type in storage_bounds
    with pytest.raises(Exception) as exc_info:
        system_design._validate_variable_config(
            stream_file=os.path.join(data_folder, 'stream_with_sediment.geojson'),
            dam_number=dam_number,
            storage_bounds=(1.5, 50),
            storage_multiplier=storage_multiplier
        )
    assert exc_info.value.args[0] == 'Each value in storage_bounds must be an integer, but got 1.5 of type "float"'

    # error test for invalid value type in storage_bounds
    with pytest.raises(Exception) as exc_info:
        system_design._validate_variable_config(
            stream_file=os.path.join(data_folder, 'stream_with_sediment.geojson'),
            dam_number=dam_number,
            storage_bounds=(1.5, 50),
            storage_multiplier=storage_multiplier
        )
    assert exc_info.value.args[0] == 'Each value in storage_bounds must be an integer, but got 1.5 of type "float"'

    # error test for value less than 1 in storage_bounds
    with pytest.raises(Exception) as exc_info:
        system_design._validate_variable_config(
            stream_file=os.path.join(data_folder, 'stream_with_sediment.geojson'),
            dam_number=dam_number,
            storage_bounds=(0, 50),
            storage_multiplier=storage_multiplier
        )
    assert exc_info.value.args[0] == 'Each value in storage_bounds must be greater than or equal to 1, but received 0'

    # error test for minimum is greater than maximum in storage_bounds
    with pytest.raises(Exception) as exc_info:
        system_design._validate_variable_config(
            stream_file=os.path.join(data_folder, 'stream_with_sediment.geojson'),
            dam_number=dam_number,
            storage_bounds=(10, 5),
            storage_multiplier=storage_multiplier
        )
    assert exc_info.value.args[0] == 'The lower bound 10 must be strictly less than the upper bound 5 in storage_bounds'

    # error test for storage_multiplier less than 0
    with pytest.raises(Exception) as exc_info:
        system_design._validate_variable_config(
            stream_file=os.path.join(data_folder, 'stream_with_sediment.geojson'),
            dam_number=dam_number,
            storage_bounds=storage_bounds,
            storage_multiplier=-1000
        )
    assert exc_info.value.args[0] == 'storage_multiplier must be greater than 0, but received -1000'

    # error test for dam number cannot be exceeded stream segments
    with pytest.raises(Exception) as exc_info:
        system_design._validate_variable_config(
            stream_file=os.path.join(data_folder, 'stream_with_sediment.geojson'),
            dam_number=50,
            storage_bounds=storage_bounds,
            storage_multiplier=storage_multiplier
        )
    assert exc_info.value.args[0] == 'dam_number 50 is out of range; expected 1 <= dam_number < 33'

    # error test for invalid model_config key type
    with pytest.raises(Exception) as exc_info:
        system_design._validate_model_config(
            model_config={1: 5}
        )
    assert exc_info.value.args[0] == 'Key "1" in model_config must be a string, but got type "int"'

    # error test for invalid model_config key name
    with pytest.raises(Exception) as exc_info:
        system_design._validate_model_config(
            model_config={'invalid_key': 5}
        )
    assert exc_info.value.args[0] == f'Invalid variable "invalid_key" in model_config; valid names are {valid_modelconfig}'

    # error test for required key in algorithm_config
    with pytest.raises(Exception) as exc_info:
        system_design._validate_algorithm_config(
            algorithm_name='NSGA5',
            algorithm_config=algorithm_config
        )
    assert exc_info.value.args[0] == f'Invalid genetic algorithm name "NSGA5"; valid names are {valid_algorithms}'

    # error test for invalid key name in algorithm_config
    with pytest.raises(Exception) as exc_info:
        system_design._validate_algorithm_config(
            algorithm_name='NSGAII',
            algorithm_config={'invalid_key': 1}
        )
    assert exc_info.value.args[0] == f'Invalid variable "invalid_key" in algorithm_config; valid names are {valid_algorithmargs}'

    # error test for required key in algorithm_config
    with pytest.raises(Exception) as exc_info:
        system_design._validate_algorithm_config(
            algorithm_name='NSGAII',
            algorithm_config={'archive': []}
        )
    assert exc_info.value.args[0] == 'Required key "population_size" is missing in algorithm_config'

    # error test for invalid value type of required key in model_config
    with pytest.raises(Exception) as exc_info:
        system_design._validate_algorithm_config(
            algorithm_name='NSGAII',
            algorithm_config={'population_size': '10'}
        )
    assert exc_info.value.args[0] == 'Value for "population_size" must be an integer, but got type "str"'

    # error test for required key in model_config
    with pytest.raises(Exception) as exc_info:
        system_design._validate_model_config(
            model_config={'year_limit': 5}
        )
    assert exc_info.value.args[0] == 'Required key "sediment_density" is missing from model_config'

    # error test for invalid objective name
    with pytest.raises(Exception) as exc_info:
        system_design._validate_objectives(
            objectives=['no_lifespan']
        )
    assert exc_info.value.args[0] == f'Invalid objective "no_lifespan"; valid names are {valid_objectives}'

    # error test for empty objective list
    with pytest.raises(Exception) as exc_info:
        system_design._validate_objectives(
            objectives=[]
        )
    assert exc_info.value.args[0] == '"objectives" cannot be an empty list'

    # error test for duplicate name in objective list
    with pytest.raises(Exception) as exc_info:
        duplicate_objectives = ['lifespan'] * 2
        system_design._validate_objectives(
            objectives=duplicate_objectives
        )
    assert exc_info.value.args[0] == f'Duplicate names found in objective list: {duplicate_objectives}'

    # error test for empty constraint dictionary
    with pytest.raises(Exception) as exc_info:
        system_design._validate_constraints(
            constraints={}
        )
    assert exc_info.value.args[0] == '"constraints" cannot be an empty dictionary'

    # error test for invalid contraint name
    with pytest.raises(Exception) as exc_info:
        system_design._validate_constraints(
            constraints={'invalid_constraint': 1}
        )
    assert exc_info.value.args[0] == f'Invalid constraint "invalid_constraint"; valid names are {valid_constraints}'

    # error test for empty constraint dictionary
    with pytest.raises(Exception) as exc_info:
        system_design._validate_constraints(
            constraints={'lb_lifespan': '1'}
        )
    assert exc_info.value.args[0] == 'Value of key "lb_lifespan" in "constraints" must be numeric, but got type "str"'
